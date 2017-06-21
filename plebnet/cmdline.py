import os
import subprocess
import sys
from argparse import ArgumentParser

from plebnet.agent.dna import DNA
from plebnet.cloudomatecontroller import options
from plebnet.config import PlebNetConfig

TRIBLER_HOME = "/root/tribler"
PLEBNET_CONFIG = "/root/.plebnet.cfg"
TIME_IN_DAY = 60.0 * 60.0 * 24.0
MAX_DAYS = 5


def execute(cmd=sys.argv[1:]):
    parser = ArgumentParser(description="Plebnet")

    subparsers = parser.add_subparsers(dest="command")
    add_parser_check(subparsers)

    args = parser.parse_args(cmd)
    args.func(args)


def add_parser_check(subparsers):
    parser_list = subparsers.add_parser("check", help="Check plebnet")
    parser_list.set_defaults(func=check)


def check(args):
    """
    Check whether conditions for buying new server are met and proceed if so
    :param args: 
    :return: 
    """
    print("Checking")
    config = PlebNetConfig.load()

    dna = DNA()
    dna.read_dictionary()

    if not tribler_running():
        print("Tribler not running")
        start_tribler()

    if config.time_since_offer() > TIME_IN_DAY:
        print("Updating daily offer")
        chosen_est_price = update_choice(config, dna)
        config.save()
        place_offer(config, chosen_est_price)

    if get_btc_balance() >= get_choice_estimate(config):
        print("Purchase server")
        purchase_choices(config)

    if uninstalled_server_available(config):
        install_server(config)


def tribler_running():
    """
    Check if tribler is running.
    :return: True if twistd.pid exists in /root/tribler
    """
    return os.path.exists(os.path.join(TRIBLER_HOME, '/twistd.pid'))


def start_tribler():
    """
    Start tribler
    :return: 
    """
    return subprocess.call(['twistd', 'plebnet', '-p', '8085', '--exitnode'], cwd=TRIBLER_HOME)


def is_evolve_ready():
    """
    Determine whether the pleb is ready to evolve
    :return: 
    """
    return True


def evolve():
    """
    Execute the commands required to evolve
    :return: 
    """
    # Load DNA
    dna = DNA()
    dna.read_dictionary()

    config = PlebNetConfig.load()
    config.get('')
    providers = dna.choose()

    # sell mc at transaction cost
    # buy servers
    # wait until both fail/succeed
    # adjust dna evolve based on success
    # create children


def update_choice(config, dna):
    choices = []
    est_btc_price = 0.0
    all_providers = dna.dictionary
    excluded_providers = config.get('excluded_providers')
    providers = {k: all_providers[k] for k in all_providers if k in all_providers.keys() - set(excluded_providers)}
    if providers >= 1:
        provider = DNA.choose_provider(providers)
        option, price = pick_option(provider)
        est_btc_price = est_btc_price + price
        choices.append((provider, option))
        del providers[provider]

    if config.time_to_expiration() > MAX_DAYS * TIME_IN_DAY and len(providers) >= 1:
        # if more than 5 days left, pick another, to improve margins
        provider = DNA.choose_provider(providers)
        option, price = pick_option(provider)
        est_btc_price = est_btc_price + price
        choices.append((provider, option))
    config.set('chosen_providers', choices)
    return est_btc_price


def pick_option(provider):
    """
    Pick most favorable option at a provider. For now pick most bandwidth per bitcoin
    :param provider: 
    :return: 
    """
    vpsoptions = options(provider)
    values = []
    for item in vpsoptions:
        bandwidth = item.bandwidth
        if isinstance(bandwidth, str):
            bandwidth = item.connection * 30 * TIME_IN_DAY
        values.append(bandwidth / item.price)
    value, option = max((v, i) for (i, v) in enumerate(values))
    return option


def place_offer(config, chosen_est_price):
    # get available mc and put this amount of mc on market for required BTC in choices
    #
    pass


def get_btc_balance():
    # return btc balance of wallet
    pass


def get_choice_estimate():
    # return estimated price for all choices or lowest of choices?
    pass


def purchase_choices(config):
    # purchase one of choices from config.get('choices') if balance is sufficient
    # after succesfull buy move this choice to the bought but not installed category

    pass


def uninstalled_server_available(config):
    pass


def install_server(config):
    pass


if __name__ == '__main__':
    execute()
