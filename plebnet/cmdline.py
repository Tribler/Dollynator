import sys
from argparse import ArgumentParser


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
    print("Checking")


if __name__ == '__main__':
    execute()
