"""
This twistd plugin enables to start Tribler headless using the twistd command.
It sets up all services needed by the PlebNet agent.

TODO: go through it thorougly
"""
from datetime import date
import os
import signal
import time

from twisted.application.service import MultiService, IServiceMaker
from twisted.conch import manhole_tap
from twisted.internet import reactor
from twisted.plugin import IPlugin
from twisted.python import usage
from twisted.python.log import msg
from zope.interface import implements

from Tribler.Core.Modules.process_checker import ProcessChecker
from Tribler.Core.Session import Session
from Tribler.Core.SessionConfig import SessionStartupConfig

# Register yappi profiler
from Tribler.community.allchannel.community import AllChannelCommunity
from Tribler.community.search.community import SearchCommunity
from Tribler.dispersy.utils import twistd_yappi


class Options(usage.Options):
    optParameters = [
        ["manhole", "m", 0, "Enable manhole telnet service listening at the specified port", int],
        ["statedir", "s", None, "Use an alternate statedir", str],
        ["restapi", "p", -1, "Use an alternate port for the REST API", int],
        ["dispersy", "d", -1, "Use an alternate port for Dispersy", int],
        ["libtorrent", "l", -1, "Use an alternate port for libtorrent", int],
    ]
    optFlags = [
        ["exitnode", "e", "Setup tribler as exitnode"],
        ["testnet", "t", "Use bitcoin testnet"],
        ["dummy", "f", "Use dummy wallets"],
    ]


class TriblerServiceMaker(object):
    implements(IServiceMaker, IPlugin)
    tapname = "plebnet"
    description = "headless tribler for plebnet agent"
    options = Options

    def __init__(self):
        """
        Initialize the variables of the TriblerServiceMaker and the logger.
        """
        self.session = None
        self._stopping = False
        self.process_checker = None

    def shutdown_process(self, shutdown_message, code=1):
        msg(shutdown_message)
        reactor.addSystemEventTrigger('after', 'shutdown', os._exit, code)
        reactor.stop()

    def start_tribler(self, options):
        """
        Main method to startup Tribler.
        """
        def on_tribler_shutdown(_):
            msg("Tribler shut down")
            reactor.stop()
            self.process_checker.remove_lock_file()

        def signal_handler(sig, _):
            msg("Received shut down signal %s" % sig)
            if not self._stopping:
                self._stopping = True
                self.session.shutdown().addCallback(on_tribler_shutdown)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        config = SessionStartupConfig().load()  # Load the default configuration file

        # Enable market_community
        config.set_market_community_enabled(True)

        # Enable exitnode if set in options
        if "exitnode" in options and options["exitnode"]:
            msg("Enabling exitnode")
            config.set_tunnel_community_exitnode_enabled(True)
        else:
            config.set_tunnel_community_exitnode_enabled(False)

        # Enable bitcoin testnet
        if "testnet" in options and options["testnet"]:
            msg("Enabling bitcoin testnet")
            config.set_btc_testnet(True)

        # Enable dummy wallets
        if "dummy" in options and options["dummy"]:
            msg("Enabling dummy wallets")
            config.set_enable_dummy_wallets(True)

        # Minimize functionality enabled for plebnet
        # For now, config taken from market_plugin in devos tribler repo
        config.set_http_api_enabled(True)
        config.set_enable_multichain(True)
        config.set_dispersy(True)
        config.set_megacache(True)  #required by dispersy
        config.set_mainline_dht(True)

        # Set false in devos tribler repo
        config.set_torrent_checking(False)
        config.set_multicast_local_peer_discovery(False)
        config.set_torrent_collecting(False)
        config.set_dht_torrent_collecting(False)
        config.set_videoserver_enabled(False)
        config.set_enable_torrent_search(False)
        config.set_enable_channel_search(False)

        # Other options that may be set
        #config.set_libtorrent()
        #config.set_torrent_store()
        #config.set_nickname("PlebNet")
        #config.set_mugshot("binary image/jpeg")
        #config.set_channel_community_enabled()
        #config.set_preview_channel_community_enabled()
        config.set_upgrader_enabled(False)
        config.set_watch_folder_enabled(False)
        #config.set_creditmining_enable()

        # Check if we are already running a Tribler instance
        self.process_checker = ProcessChecker()
        if self.process_checker.already_running:
            self.shutdown_process("Another Tribler instance is already using statedir %s" % config.get_state_dir())
            return

        msg("Starting Tribler")

        if options["statedir"]:
            config.set_state_dir(options["statedir"])

        if options["restapi"] > 0:
            config.set_http_api_enabled(True)
            config.set_http_api_port(options["restapi"])

        if options["dispersy"] > 0:
            config.set_dispersy_port(options["dispersy"])

        if options["libtorrent"] > 0:
            config.set_listen_port(options["libtorrent"])

        self.session = Session(config)
        self.session.start().addErrback(lambda failure: self.shutdown_process(failure.getErrorMessage()))
        msg("Tribler started")

        if "auto-join-channel" in options and options["auto-join-channel"]:
            msg("Enabling auto-joining of channels")
            for community in self.session.get_dispersy_instance().get_communities():
                if isinstance(community, AllChannelCommunity):
                    community.auto_join_channel = True

    def makeService(self, options):
        """
        Construct a Tribler service.
        """
        tribler_service = MultiService()
        tribler_service.setName("Tribler")

        manhole_namespace = {}
        if options["manhole"] > 0:
            port = options["manhole"]
            manhole = manhole_tap.makeService({
                'namespace': manhole_namespace,
                'telnetPort': 'tcp:%d:interface=127.0.0.1' % port,
                'sshPort': None,
                'passwd': os.path.join(os.path.dirname(__file__), 'passwd'),
            })
            tribler_service.addService(manhole)

        reactor.callWhenRunning(self.start_tribler, options)

        return tribler_service

service_maker = TriblerServiceMaker()
