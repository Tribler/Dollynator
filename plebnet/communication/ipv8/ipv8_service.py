import binascii

from jsonrpclib.jsonrpc import json
from twisted.internet import reactor, endpoints
from twisted.web import server, resource
from twisted.internet.task import LoopingCall

from pyipv8.ipv8.community import Community
from pyipv8.ipv8.messaging.payload import Payload
from pyipv8.ipv8.messaging.payload_headers import BinMemberAuthenticationPayload, GlobalTimeDistributionPayload
from pyipv8.ipv8_service import IPv8
from pyipv8.ipv8.configuration import get_default_configuration
from pyipv8.ipv8.peer import Peer


# Message definitions
MSG_HELLO = 1


class HelloMessage(Payload):
    format_list = ['raw']

    def __init__(self, value):
        self.value = value

    def to_pack_list(self):
        return [('raw', self.value)]

    @classmethod
    def from_unpack_list(cls, value):
        return cls(value)


class HelloAPIResource(resource.Resource):
    isLeaf = True

    def render_GET(self, request):
        community = ipv8.overlays[0]

        # send hello to all peers
        peers = community.get_peers()
        for peer in peers:
            message = community.create_hello_message()
            print("send " + str(message) + " to " + str(peer.address))
            ipv8.endpoint.send(peer.address, message)

        request.setHeader(b"content-type", b"text/json")
        response = {"peer_count": len(peers)}
        return json.dumps(response)


class PlebNetCommunity(Community):
    # Register this community with a master peer.
    # This peer defines the service identifier of this community.
    # Other peers will connect to this community based on the sha-1
    # hash of this peer's public key.
    # master_key = ECCrypto().generate_key(u"medium")
    # print('master_key: ' + binascii.hexlify(master_key.pub().key_to_bin()))
    master_key = "307e301006072a8648ce3d020106052b81040024036a000400bd5e1a3ee8e6990bb241921cd1aa334be4c922c8a5952b" \
                 "568ba20066982ddad2cf7ddf773ba36ae6d963f8a26c8452cfb444be003c8a40055f03692039f4a4ee431e2b45a44da0" \
                 "887278591b429a6dd931b66e9190b850a4c5b7b4ea3feb7f38665896003209c5".decode("hex")
    master_peer = Peer(master_key)

    def __init__(self, my_peer, endpoint, network):
        super(PlebNetCommunity, self).__init__(my_peer, endpoint, network)
        # Register the message handler for messages with the
        # chr(1) identifier.
        self.decode_map[chr(MSG_HELLO)] = self.on_hello_message

    def started(self):
        def print_peers():
            print "I am:", self.my_peer, "\nI know:", [str(p) for p in self.get_peers()]

        # We register a Twisted task with this overlay.
        # This makes sure that the task ends when this overlay is unloaded.
        # We call the 'print_peers' function every 5.0 seconds, starting now.
        self.register_task("print_peers", LoopingCall(print_peers)).start(5.0, True)

    def on_hello_message(self, source_address, data):
        # We received a message with identifier 1.
        # Try unpacking it.
        auth, dist, payload = self._ez_unpack_auth(HelloMessage, data)
        print 'received ' + str(payload) + ' from ' + str(source_address)

    def create_hello_message(self):
        # Create a message with our digital signature on it.
        auth = BinMemberAuthenticationPayload(self.my_peer.public_key.key_to_bin()).to_pack_list()
        dist = GlobalTimeDistributionPayload(self.claim_global_time()).to_pack_list()
        payload = HelloMessage('hello').to_pack_list()
        # We pack our arguments as message 1 (corresponding to the
        # 'self.decode_map' entry.
        return self._ez_pack(self._prefix, MSG_HELLO, [auth, dist, payload])


configuration = get_default_configuration()

# If we actually want to communicate between two different peers
# we need to assign them different keys.
# We will generate an EC key called 'bot' which has 'medium'
# security and will be stored in file 'ec.pem'
configuration['keys'] = [{
    'alias': "bot",
    'generation': u"medium",
    'file': u"ec.pem"
}]

# Instruct IPv8 to load our custom overlay, registered in _COMMUNITIES.
# We use the 'bot' key, which we registered before.
# We will attempt to find other peers in this overlay using the
# RandomWalk strategy, until we find 10 peers.
# We do not provide additional startup arguments or a function to run
# once the overlay has been initialized.
configuration['overlays'] = [{
    'class': 'PlebNetCommunity',
    'key': "bot",
    'walkers': [{
        'strategy': "RandomWalk",
        'peers': 10,
        'init': {
            'timeout': 3.0
        }
    }],
    'initialize': {},
    'on_start': [('started',)]
}]

ipv8 = IPv8(configuration, extra_communities={'PlebNetCommunity': PlebNetCommunity})

api = resource.Resource()
api.putChild('hello', HelloAPIResource())
endpoints.serverFromString(reactor, "tcp:8090").listen(server.Site(api))

reactor.run()
