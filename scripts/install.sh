#!/usr/bin/env bash

# Add locale
echo 'LANG=en_US.UTF-8' > /etc/locale.conf
locale-gen en_US.UTF-8

# No interactivity
DEBIAN_FRONTEND=noninteractive
echo force-confold >> /etc/dpkg/dpkg.cfg
echo force-confdef >> /etc/dpkg/dpkg.cfg

# Upgrade system
apt-get update
# Do not upgrade for now as in some VPS it will cause for example grub to update
# Requiring manual configuration after installation
# && apt-get -y upgrade


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
    python-pip \
    python-lxml

# Update pip to avoid locale errors in certain configurations
echo "upgrading pip"
LC_ALL=en_US.UTF-8 pip install --upgrade pip
echo "done upgrading pip"

pip install pyaes psutil

cd $HOME
[ ! -d "PlebNet" ] && git clone -b master https://github.com/rjwvandenberg/PlebNet
pip install --upgrade ./PlebNet
cd PlebNet
git submodule update --init --recursive tribler
pip install ./tribler/electrum
#no longer used since importing own tribler fork
#cp docker/market/twistd_plugin/plebnet_plugin.py $HOME/PlebNet/tribler/twisted/plugins/
cd /root
plebnet setup >> plebnet.log 2>> plebnet.err

# cron plebnet check
echo "*/2 * * * * root /usr/local/bin/plebnet check >> plebnet.log 2>> plebnet.err" > /etc/cron.d/plebnet
