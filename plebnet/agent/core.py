"""
A package which handles the main behaviour of the plebbot:
- check if everything is up and running
- check if the configuration is all set properly
- check if a new child can be spawned and do so if possible
"""

import os
import subprocess
import time

from plebnet.agent.dna import DNA
from plebnet.agent.config import PlebNetConfig
from plebnet.clone import server_installer
from plebnet.controllers import tribler_controller, cloudomate_controller, market_controller, electrum_controller
from plebnet.communication.irc import irc_handler
from plebnet.settings import plebnet_settings
from plebnet.utilities import logger, fake_generator


setup = plebnet_settings.get_instance()
log_name = "agent.core"  # used for identifying the origin of the log message
config = None  # Used to store the configuration and only load once
dna = None  # Used to store the DNA of the agent and only load once


def setup(args):
    logger.log("Setting up PlebNet")

    # Prepare Cloudomate
    if args.test_net:
        logger.warning("should use fake money, but not implemented yet", "setup")
    fake_generator.generate_child_account()

    # TODO: change --> Prepare plebnet
    config = PlebNetConfig()
    config.set('expiration_date', time.time() + 30 * plebnet_settings.TIME_IN_DAY)
    config.save()

    # handle the DNA
    dna = DNA()
    dna.read_dictionary(cloudomate_controller.get_vps_providers())
    dna.write_dictionary()

    # Prepare Electrum
    electrum_controller.create_wallet()

    # Prepare the IRC Client
    irc_handler.init_irc_client()
    irc_handler.start_irc_client()

    logger.success("PlebNet is ready to roll!")


def check():
    """
    The main function to run every interval
    :return: None
    :rtype: None
    """
    global config, dna

    logger.log("Checking PlebNet", log_name)
    config = PlebNetConfig()

    # TODO: DNA static singular maken --> dan kan dit weg
    dna = DNA()
    dna.read_dictionary()

    # these require time to setup, continue in the next iteration
    if not check_tribler():
        return
    if not check_tunnel_helper():
        return

    select_provider()
    update_offer()
    attempt_purchase()
    install_vps()


def check_tribler():
    """
    Check whether Tribler is running and configured properly
    :return: True if tribler is running, False otherwise
    :rtype: Boolean
    """
    if tribler_controller.running():
        logger.log("Tribler is already running", log_name)
        return True
    else:
        tribler_controller.start()
        return False


def check_tunnel_helper():
    """
    Temporary function to track the data stream processed by Tribler
    :return: None
    :rtype: None
    """
    # TEMP TO SEE EXITNODE PERFORMANCE, tunnel_helper should merge with market or other way around
    if not os.path.isfile(os.path.join(setup.get_tribler_home(), setup.get_tunnelhelper_pid())):
        logger.log("Starting tunnel_helper", log_name)
        env = os.environ.copy()
        env['PYTHONPATH'] = setup.get_tribler_home()
        try:
            subprocess.call(['twistd', '--pidfile='+setup.get_tunnelhelper_pid(), 'tunnel_helper', '-x', '-M'],
                            cwd=setup.get_tribler_home(), env=env)
            return True
        except subprocess.CalledProcessError as e:
            logger.error(e.output, log_name)
            return False
    return True
    # TEMP TO SEE EXITNODE PERFORMANCE


def update_offer():
    """
    check if the stored prices for the selected provider should be updated.
    This does not have to happen every iteration as they do not change that often
    :return: None
    :rtype: None
    """
    if config.time_since_offer() > plebnet_settings.TIME_IN_HOUR:
        logger.log("Calculating new offer", log_name)
        cloudomate_controller.update_offer(config)
        config.save()


def attempt_purchase():
    """
    Check if rich enough to buy a server, and if so, do so
    :return: None
    :rtype: None
    """
    # try to purchase the chosen vps.
    (provider, option, _) = config.get('chosen_provider')
    if market_controller.get_btc_balance() >= cloudomate_controller.calculate_price(provider, option):
        logger.log("Try to buy a new server from %s" % provider, log_name)
        success = cloudomate_controller.purchase_choice(config)
        if success == setup.SUCCESS:
            # evolve yourself positively if you are successful
            own_provider = DNA.get_own_provider(dna)
            DNA.evolve(own_provider, dna, True)
        elif success == setup.FAILURE:
            # evolve provider negatively if not successful
            DNA.evolve(provider, dna, False)


def install_vps():
    """
    Tries to install all purchased servers, can be skipped if the server is not configured yet.
    :return: None
    :rtype: None
    """
    server_installer.install_available_servers(config, dna)


# TODO: dit moet naar agent.DNA, maar die is nu al te groot
def select_provider():
    """
    Check whether a provider is already selected, otherwise select one based on the dna
    :return: None
    :rtype: None
    """
    if not config.get('chosen_provider'):
        logger.log("No provider chosen yet", log_name)

        all_providers = dna.vps
        excluded_providers = config.get('excluded_providers')
        available_providers = list(set(all_providers.keys()) - set(excluded_providers))
        providers = {k: all_providers[k] for k in all_providers if k in available_providers}

        if providers >= 1 and sum(providers.values()) > 0:
            providers = DNA.normalize_excluded(providers)
            choice = cloudomate_controller.pick_provider(providers)
            config.set('chosen_provider', choice)
        logger.log("Provider chosen: %s" % str(config.get('chosen_provider')), log_name)
        config.save()
