"""
A package which handles the main behaviour of the PlebNet agent:
- Set all configuration files.
- Check if Tribler and the Tribler Marketplace are running.
- Create the necessary wallets.
- Check if a new child agent can be bought and do so if possible.
"""

import os
import random
import time
import re
import subprocess
import shutil

from plebnet.agent.dna import DNA
from plebnet.agent.config import PlebNetConfig
from plebnet.clone import server_installer
from plebnet.controllers import tribler_controller, cloudomate_controller, market_controller, wallet_controller
from plebnet.communication.irc import irc_handler
from plebnet.settings import plebnet_settings
from plebnet.utilities import logger, fake_generator


settings = plebnet_settings.get_instance()
log_name = "agent.core"  # Used for identifying the origin of the log message.
config = None  # Used to store the configuration and only load once.
dna = None  # Used to store the DNA of the agent and only load once.


def setup(args):
    """
    This method should only be called once and is responsible for the initial setup of the PlebNet
    agent. All necessary configuration files are created and IRC communication is started.
    :param args: If running in Testnet mode.
    """
    global dna, config
    logger.log("Setting up PlebNet")

    # Prepare the DNA configuration
    dna = DNA()

    if args.test_net:
        settings.wallets_testnet("1")
        settings.settings.write()
        dna.read_dictionary({'proxhost': cloudomate_controller.get_vps_providers()['proxhost']})
    else:
        dna.read_dictionary(cloudomate_controller.get_vps_providers())
        if 'proxhost' in dna.vps.keys():
            dna.remove_provider('proxhost')
    dna.write_dictionary()

    if args.exit_node:
        logger.log("Running as exitnode")
        settings.tribler_exitnode('1')

    # Prepare first child configuration
    fake_generator.generate_child_account()

    # Set general info about the PlebNet agent
    settings.irc_nick(settings.irc_nick_def() + str(random.randint(1000, 10000)))
    config = PlebNetConfig()
    config.set('expiration_date', time.time() + 30 * plebnet_settings.TIME_IN_DAY)

    # Prepare the IRC Client
    irc_handler.init_irc_client()
    irc_handler.start_irc_client()

    if dna.get_own_tree() == '':
        logger.log("tree set to %s" % settings.irc_nick())
        dna.set_own_tree(settings.irc_nick())

    config.save()

    logger.success("PlebNet is ready to roll!")


def check():
    """
    The method is the main function which should run periodically. It controls the behaviour of the agent,
    starting Tribler and buying servers.
    """
    global config, dna
    logger.log("Checking PlebNet", log_name)

    # Read general configuration
    if settings.wallets_testnet_created():
        os.environ['TESTNET'] = '1'
    config = PlebNetConfig()
    dna = DNA()
    dna.read_dictionary()

    # check if own vpn is installed before continuing
    if not check_vpn_install():
        logger.error("!!! VPN is not installed, child may get banned !!!", "Plebnet Check")

    # Requires time to setup, continue in the next iteration.
    if not check_tribler():
        return

    if not settings.wallets_initiate_once():
        create_wallet()
    select_provider()

    # These need a matchmaker, otherwise agent will be stuck waiting.
    if market_controller.has_matchmakers():
        update_offer()
        attempt_purchase()
    install_vps()


def create_wallet():
    """
    Checks if a Bitcoin (BTC) wallet or a Testnet Bitcoin (TBTC) wallet needs to be made.
    """
    if settings.wallets_testnet():
        # Attempt to create Testnet wallet
        logger.log("create Testnet wallet")
        x = wallet_controller.create_wallet('TBTC')
        if x:
            settings.wallets_testnet_created("1")
            settings.wallets_initiate_once("1")
            settings.settings.write()
            os.environ['TESTNET'] = '1'
    else:
        # Attempt to create Bitcoin wallet
        logger.log("create Bitcoin wallet")
        y = wallet_controller.create_wallet('BTC')
        if y:
            settings.wallets_initiate_once("1")
            settings.settings.write()


def check_tribler():
    """
    Check whether Tribler is running and configured properly, otherwise start Tribler.
    :return: True if tribler is running, False otherwise.
    :rtype: Boolean
    """
    if tribler_controller.running():
        logger.log("Tribler is already running", log_name)
        return True
    else:
        tribler_controller.start()
        return False


def check_vpn_install():
    """
    Checks the vpn configuration files (.ovpn, credentials.conf).
    If configuration files exist, no need to purchase VPN configurations.
    :return: True if installing succeeds, False if installing fails or configs are not found
    """
    # chech whether vpn is installed
    if vpn_is_running():
        logger.log("VPN is already installed and running.")
        return True

    # check OWN configuration files.
    credentials = os.path.join(os.path.expanduser(settings.vpn_config_path()),
                               settings.vpn_own_prefix()+settings.vpn_credentials_name())
    vpnconfig = os.path.join(os.path.expanduser(settings.vpn_config_path()),
                             settings.vpn_own_prefix()+settings.vpn_config_name())

    if os.path.isfile(credentials) and os.path.isfile(vpnconfig):
        # try to install
        if install_vpn():
            time.sleep(30)
            settings.vpn_installed("1")
            logger.log("Installing VPN succesful with configurations.")
            if irc_handler.restart_irc_client():
                logger.log("Restarted IRC because VPN was installed.")
            return True
        else:
            settings.vpn_installed("0")
            logger.log("Installing VPN failed with configurations. Subscription passed?")
            return False
    else:
        logger.log("No VPN configurations found!")
        return False


def attempt_purchase_vpn():
    """
    Attempts to purchase a VPN, checks first if balance is sufficient
    The success message is stored to prevent further unecessary purchases.
    """
    provider = settings.vpn_host()
    if settings.wallets_testnet():
        domain = 'TBTC'
    else:
        domain = 'BTC'
    if market_controller.get_balance(domain) >= cloudomate_controller.calculate_price_vpn(provider):
        logger.log("Try to buy a new VPN from %s" % provider, log_name)
        success = cloudomate_controller.purchase_choice_vpn(config)
        if success == plebnet_settings.SUCCESS:
            logger.success("Purchasing VPN succesful!", log_name)
        elif success == plebnet_settings.FAILURE:
            logger.error("Error purchasing vpn", log_name)


def update_offer():
    """
    Check if an hour as passed since the last offer made, if passed calculate a new offer.
    """
    if config.time_since_offer() > plebnet_settings.TIME_IN_HOUR:
        logger.log("Calculating new offer", log_name)
        cloudomate_controller.update_offer(config)
        config.save()


def attempt_purchase():
    """
    Check if enough money to buy a server, and if so, do so,
    """
    (provider, option, _) = config.get('chosen_provider')
    if settings.wallets_testnet():
        domain = 'TBTC'
    else:
        domain = 'BTC'
    if market_controller.get_balance(domain) >= (cloudomate_controller.calculate_price(provider, option) +
                                                 cloudomate_controller.calculate_price_vpn()):
        logger.log("Try to buy a new server from %s" % provider, log_name)
        success = cloudomate_controller.purchase_choice(config)
        if success == plebnet_settings.SUCCESS:
            # Evolve yourself positively if you are successful
            dna.evolve(True)
            logger.log("Purchasing vps for child %s successful"%(dna.get_own_tree()+'.'+str(config.get('child_index'))))
            # purchase VPN with same config if server allows for it
            if cloudomate_controller.get_vps_providers()[provider].TUN_TAP_SETTINGS:
                attempt_purchase_vpn()
        elif success == plebnet_settings.FAILURE:
            # Evolve provider negatively if not successful
            dna.evolve(False, provider)

        config.increment_child_index()
        fake_generator.generate_child_account()
        config.set('chosen_provider', None)
        config.save()


def install_vps():
    """
    Calls the server install for installing all purchased servers.
    """
    server_installer.install_available_servers(config, dna)


def install_vpn():
    """
    Attempts to install the vpn using the credentials.conf and .ovpn configuration files
    :return: True if installing succeeded, otherwise it will raise an exception.
    """

    logger.log("Installing VPN")

    # configuring nameservers, if the server uses a local nameserver
    # either 1.1.1.1/1.0.0.1 or 8.8.8.8/8.8.4.4 work
    resolv = """nameserver 1.1.1.1
    nameserver 1.0.0.1"""

    with open(os.path.expanduser('/etc/resolv.conf'), 'w') as dnsfile:
        dnsfile.write(resolv)
    vpnconfig = os.path.join(os.path.expanduser(settings.vpn_config_path()),
                             settings.vpn_own_prefix() + settings.vpn_config_name())
    try_install = subprocess.Popen('openvpn --config ' + vpnconfig + ' --daemon',
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True,
                                   cwd=os.path.expanduser('~/'))

    result, error = try_install.communicate()
    exitcode = try_install.wait()

    time.sleep(30)

    if exitcode != 0:
        if error.decode('ascii') == "":
            error = result
        logger.log("ERROR installing VPN, Code: " + str(exitcode) + " - Message: " + error.decode('ascii'))
        return False
    else:
        pid = str(try_install.pid)
        settings.vpn_pid(pid)
        settings.vpn_running("1")
        return True


def vpn_is_running():
    """
    :return: True if vpn is running, else false
    """
    # pid is currently not used as the pid changes when openvpn has started.
    pid = settings.vpn_pid()
    check = subprocess.call(['ps', '-C', 'openvpn'])
    if check == 0:
        settings.vpn_running("1")
        return True
    else:
        settings.vpn_running("0")
        settings.vpn_pid(0)
        return False


# TODO: dit moet naar agent.DNA, maar die is nu al te groot
def select_provider():
    """
    Check whether a provider is already selected, otherwise select one based on the DNA.
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
