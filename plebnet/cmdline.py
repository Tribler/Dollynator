import sys
import os
from argparse import ArgumentParser

from plebnet.agent.dna import DNA

TRIBLER_HOME = "/root/tribler"

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
    if not tribler_running():
        print("Tribler not running")
        start_tribler()
    if is_evolve_ready():
        evolve()

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
    raise NotImplementedError('Start tribler? or raise error')

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
    providers = dna.choose()

    # sell mc at transaction cost
    # buy servers
    # wait until both fail/succeed
    # adjust dna evolve based on success
    # create children


if __name__ == '__main__':
    execute()
