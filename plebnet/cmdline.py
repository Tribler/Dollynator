import sys
from argparse import ArgumentParser

from plebnet.communication.irc import irc_handler
from plebnet.settings import plebnet_settings
from plebnet.agent import core as agent


def execute(cmd=sys.argv[1:2]):
    parser = ArgumentParser(description="Plebnet - a working-class bot")
    subparsers = parser.add_subparsers(dest="command")

    # create the setup subcommand
    parser_list = subparsers.add_parser("setup", help="Run the setup of PlebNet")
    parser_list.set_defaults(func=execute_setup)

    # create the check subcommand
    parser_list = subparsers.add_parser("check", help="Checks if the plebbot is able to clone")
    parser_list.set_defaults(func=execute_check)

    # create the conf subcommand
    parser_list = subparsers.add_parser("conf", help="allows changing the configuration files")
    parser_list.set_defaults(func=execute_conf)

    # create the irc subcommand
    parser_list = subparsers.add_parser("irc", help="Provides access to the IRC client")
    parser_list.set_defaults(func=execute_irc)

    args = parser.parse_args(cmd)
    args.func()


def execute_setup(cmd=sys.argv[2:]):
    parser = ArgumentParser(description="setup thingies")
    parser.add_argument('-test', action='store_true', default=False,
                  dest='test_net',
                  help='Use test net instead of BTC')
    args = parser.parse_args(cmd)

    agent.setup(args)


def execute_check(cmd=sys.argv[2:]):
    agent.check()


def execute_conf(cmd=sys.argv[2:3]):
    parser = ArgumentParser(description="allows changing the configuration files")
    subparsers = parser.add_subparsers(dest="command", title="files")

    parser_secure = subparsers.add_parser("setup", help='this is no help')
    parser_secure.set_defaults(func=conf_secure)

    args = parser.parse_args(cmd)
    args.func()


def conf_secure(cmd=sys.argv[3:]):
    parser = ArgumentParser(description="allow changing the configuration files for logging in")
    #irc section
    parser.add_argument('-ic', '--irc_channel', help='Set the irc channel to use')
    parser.add_argument('-is', '--irc_server',  help='Set the irc server to use')
    parser.add_argument('-ip', '--irc_port',    help='Set the irc server port to use')
    parser.add_argument('-in', '--irc_nick',    help='Set the irc nickname to use')
    parser.add_argument('-it', '--irc_timeout', help='Set the irc heartbeat timeout to use')
    #github section
    parser.add_argument('-gu', '--github_username', help='Set this username')
    parser.add_argument('-gp', '--github_password', help='Set this password')
    parser.add_argument('-go', '--github_owner', help='Set this password')
    parser.add_argument('-gr', '--github_repo', help='Set this password')
    parser.add_argument('-ga', '--github_active', help='(De)activate the github issuer', choices=["0", "1"])

    args = parser.parse_args(cmd)

    plebnet_settings.store(args)


def execute_irc(cmd=sys.argv[2:]):
    parser = ArgumentParser(description="irc thingies")

    subparsers = parser.add_subparsers(dest="command")
    parser_list = subparsers.add_parser("status", help="Provides information regarding the status of the IRC Client")
    parser_list.set_defaults(func=irc_handler.status_irc_client)

    parser_list = subparsers.add_parser("start", help="Starts the IRC Client ")
    parser_list.set_defaults(func=irc_handler.start_irc_client)

    parser_list = subparsers.add_parser("stop", help="Stops the IRC Client")
    parser_list.set_defaults(func=irc_handler.stop_irc_client)

    parser_list = subparsers.add_parser("restart", help="Restarts the IRC Client ")
    parser_list.set_defaults(func=irc_handler.restart_irc_client)

    args = parser.parse_args(cmd)
    args.func(args)


if __name__ == '__main__':
    execute()
