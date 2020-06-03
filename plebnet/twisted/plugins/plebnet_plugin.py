"""
This twistd plugin enables to start Tribler headless using the twistd command.
"""
import os
import signal

from twisted.application.service import MultiService, IServiceMaker
from twisted.internet import reactor
from twisted.plugin import IPlugin
from twisted.python import usage
from twisted.python.log import msg
from zope.interface import implements, implementer

from tribler_core.config.tribler_config import TriblerConfig
from tribler_core.modules.process_checker import ProcessChecker
from tribler_core.session import Session
# Register yappi profiler
from tribler.src.anydex.anydex.core.community import MarketCommunity


class Options(usage.Options):
    optParameters = [
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


class MarketServiceMaker(object):
    implementer(IServiceMaker, IPlugin)
    tapname = "plebnet"
    description = "headless tribler for plebnet agent"
    options = Options

    def __init__(self):
        self.session = None
        self._stopping = False
        self.process_checker = None
        self.market_community = None
        self.plebmail_community = None

    def shutdown_process(self, shutdown_message, code=1):
        msg(shutdown_message)
        reactor.addSystemEventTrigger('after', 'shutdown', os._exit, code)
        reactor.stop()

    def load_communities(self, _):
        self.load_market_community(_)
        self.load_plebmail_community(_)

    def load_market_community(self, _):
        """
        Load the Market community
        """
        msg("Loading market community...")
        self.market_community = self.session.get_dispersy_instance().define_auto_load(
            MarketCommunity, self.session.dispersy_member, load=True, kargs={'tribler_session': self.session})

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

        config = TriblerConfig()

        self.process_checker = ProcessChecker()
        if self.process_checker.already_running:
            self.shutdown_process("Another Tribler instance is already using statedir %s" % config.get_state_dir())
            return

        # Enable exitnode if set in options
        if "exitnode" in options and options["exitnode"]:
            msg("Enabling exitnode")
            config.set_tunnel_community_enabled(True)
            config.set_tunnel_community_exitnode_enabled(True)
        else:
            config.set_tunnel_community_exitnode_enabled(False)

        # Enable bitcoin testnet
        if "testnet" in options and options["testnet"]:
            msg("Enabling bitcoin testnet")
            config.set_testnet(True)

        # Enable dummy wallets
        if "dummy" in options and options["dummy"]:
            msg("Enabling dummy wallets")
            config.set_dummy_wallets_enabled(True)

        # Enable record transactions
        msg("Enabling record transactions")
        config.set_record_transactions(True)

        # Minimize functionality enabled for plebnet
        # For now, config taken from market_plugin in devos tribler repo
        config.set_http_api_enabled(True)
        config.set_video_server_enabled(False)
        config.set_torrent_search_enabled(False)
        config.set_channel_search_enabled(False)
        config.set_mainline_dht_enabled(True)
        config.set_dht_enabled(True)
        config.set_chant_enabled(False)
        config.set_bitcoinlib_enabled(True)

        msg("Starting Tribler")

        if options["statedir"]:
            config.set_state_dir(options["statedir"])

        if options["restapi"] > 0:
            config.set_http_api_enabled(True)
            config.set_http_api_port(options["restapi"])

        if options["dispersy"] != -1 and options["dispersy"] > 0:
            config.set_dispersy_port(options["dispersy"])

        if options["libtorrent"] != -1 and options["libtorrent"] > 0:
            config.set_libtorrent_port(options["libtorrent"])

        self.session = Session(config)
        self.session.start().addErrback(lambda failure: self.shutdown_process(failure.getErrorMessage()))

        msg("Tribler started")

    def makeService(self, options):
        """
        Construct a Tribler service.
        """
        tribler_service = MultiService()
        tribler_service.setName("Market")

        reactor.callWhenRunning(self.start_tribler, options)

        return tribler_service


service_maker = MarketServiceMaker()
