#!/usr/bin/env bash

# Add locale
echo 'LANG=en_US.UTF-8' > /etc/locale.conf
locale-gen en_US.UTF-8

# No interactivity
DEBIAN_FRONTEND=noninteractive
echo force-confold >> /etc/dpkg/dpkg.cfg
echo force-confdef >> /etc/dpkg/dpkg.cfg

# Upgrade system
apt-get update && apt-get -y upgrade


# Install dependencies
sudo apt-get install -y \
    python-crypto \
    python-cryptography \
    python-pyasn1 \
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
pip install ./electrum

cd $HOME
[ ! -d "PlebNet" ] && git clone https://github.com/rjwvandenberg/PlebNet
pip install --upgrade ./PlebNet
cd PlebNet
cd docker/market/twistd_plugin/
cp plebnet_plugin.py ~/tribler/twisted/plugins/

cd $HOME
cd tribler
export PYTHONPATH=.
twistd plebnet -p 8085 --exitnode

plebnet setup

# cron plebnet check
echo "* * * * * root /usr/local/bin/plebnet check >> ~/plebnet.log 2>&1" > /etc/cron.d/plebnet
