import sys
from argparse import ArgumentParser

from plebnet import cloudomatecontroller, twitter


def execute(cmd=sys.argv[1:]):
    parser = ArgumentParser(description="Plebnet")

    subparsers = parser.add_subparsers(dest="command")
    add_parser_check(subparsers)
    add_parser_setup(subparsers)

    args = parser.parse_args(cmd)
    args.func(args)


def add_parser_check(subparsers):
    parser_list = subparsers.add_parser("check", help="Check plebnet")
    parser_list.set_defaults(func=check)


def add_parser_setup(subparsers):
    parser_list = subparsers.add_parser("setup", help="Setup plebnet")
    parser_list.set_defaults(func=setup)


def setup(args):
    print("Setting up PlebNet")
    cp = cloudomatecontroller.generate_config()
    twitter.tweet_arrival(cp.get('firstname') + ' ' + cp.get('lastname'))


def check(args):
    print("Checking")


if __name__ == '__main__':
    execute()
