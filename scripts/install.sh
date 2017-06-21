echo 'LANG=en_US.UTF-8' > /etc/locale.conf
locale-gen en_US.UTF-8
apt-get update && apt-get -y --force-yes upgrade

sudo apt-get install -y libav-tools libsodium18 libx11-6 python-crypto python-cryptography python-matplotlib python-pil python-pyasn1

apt-get install -y \
    python-twisted \
    python-libtorrent \
    python-apsw \
    python-chardet \
    python-cherrypy3 \
    python-nacl \
    python-m2crypto \
    python-configobj \
    python-netifaces \
    python-leveldb \
    python-decorator \
    python-feedparser \
    python-keyring \
    python-libnacl \
    python-ecdsa \
    python-pbkdf2 \
    python-requests \
    python-protobuf \
    python-socks \
    python-dnspython \
    python-jsonrpclib \
    python-keyrings.alt \
    python-networkx \
    python-scipy \
    python-wxtools \
    git \
    python-pip

pip install pyaes

cd $HOME
git clone --recursive https://github.com/devos50/tribler
cd tribler
git checkout market_community
git submodule update --init --recursive electrum
git submodule update --init --recursive Tribler/dispersy
git submodule update --init --recursive Tribler/Core/DecentralizedTracking/pymdht

cd $HOME
git clone https://github.com/rjwvandenberg/PlebNet
pip install PlebNet
cd PlebNet
cd docker/market/twistd_plugin/
cp plebnet_plugin.py ~/tribler/twisted/plugins/

cd $HOME
# sed -ie 's/"127.0.0.1"/"0.0.0.0"/g' /root/tribler/Tribler/Core/Modules/restapi/rest_manager.py
cd tribler
export PYTHONPATH=.
twistd plebnet -p 8085 --exitnode
