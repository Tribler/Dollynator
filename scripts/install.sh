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
sudo apt-get install -y python-pip
sudo apt-get install -y \
    python-crypto \
    python-pyasn1 \
    python-twisted \
    python-libtorrent \
    python-apsw \
    python-chardet \
    python-cherrypy3 \
    python-m2crypto \
    python-configobj \
    python-netifaces \
    python-leveldb \
    python-decorator \
    python-feedparser \
    python-keyring \
    python-ecdsa \
    python-pbkdf2 \
    python-requests \
    python-protobuf \
    python-dnspython \
    python-jsonrpclib \
    python-networkx \
    python-scipy \
    python-wxtools \
    git \
    python-lxml
if [ $(lsb_release -cs) == "trusty" ]
then
    echo "Trusty detected"
    sudo apt-get install -y build-essential libssl-dev libffi-dev python-dev software-properties-common
    pip install cryptography
    pip install pynacl
    pip install pysocks
    pip install keyrings.alt
    pip install libnacl
    sudo add-apt-repository -y ppa:chris-lea/libsodium;
    sudo echo "deb http://ppa.launchpad.net/chris-lea/libsodium/ubuntu trusty main" >> /etc/apt/sources.list;
    sudo echo "deb-src http://ppa.launchpad.net/chris-lea/libsodium/ubuntu trusty main" >> /etc/apt/sources.list;
    sudo apt-get update && sudo apt-get install -y libsodium-dev;
else
    apt-get install -y python-cryptography \
	python-nacl \
	python-libnacl \
	python-socks \
	keyrings.alt
fi

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
plebnet setup >> plebnet.log 2>&1

# cron plebnet check
echo "*/2 * * * * root /usr/local/bin/plebnet check >> plebnet.log 2>&1" > /etc/cron.d/plebnet
