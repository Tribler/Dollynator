import subprocess
import sys
import os
from argparse import ArgumentParser

from plebnet.agent.dna import DNA
from plebnet.config import PlebNetConfig

TRIBLER_HOME = "/root/tribler"
PLEBNET_CONFIG = "/root/.plebnet.cfg"
TIME_IN_DAY = 60.0 * 60.0 * 24.0


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
    if not tribler_running():
        print("Tribler not running")
        start_tribler()

    if config.time_since_offer() > TIME_IN_DAY:
        print("Updating daily offer")
        update_choice(config)
        config.save()
        place_offer(config)

    if get_btc_balance() >= get_choice_estimate(config):
        print("Purchase server")
        purchase_choices(config)

    # implement check for availability of bought, but not installed servers
    # if available install server


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

def update_choice(config):
    if config.time_to_expiration() <= 5*TIME_IN_DAY:
        # choose(1)
        # from randomly chosen provider pick the best available vpsoption
        pass
    else:
        # choose(2)
        # from 2 randomly chosen providers pick the best available vpsoptions
        pass
    #save the choices as (hoster, vpsoption) pairs in config.get('choices') as a list
    # return estimated price

def place_offer(config):
    # get available mc and put this amount of mc on market for required BTC in choices
    #
    pass

def get_btc_balance():
    #return btc balance of wallet
    pass

def get_choice_estimate():
    # return estimated price for all choices or lowest of choices?
    pass

def purchase_choices(config):
    #purchase one of choices from config.get('choices') if balance is sufficient
    #after succesfull buy move this choice to the bought but not installed category

    pass


if __name__ == '__main__':
    execute()
