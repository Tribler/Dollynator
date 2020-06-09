#!/usr/bin/env bash

#exec 3>&1 4>&2
#trap 'exec 2>&4 1>&3' 0 1 2 3
#exec 1>install_$(date +'%Y%m%dT%H%M%S').log 2>&1

#
# This file is called from the parent node together with the rest of the files from GitHub.
#
# It downloads all dependencies for this version of PlebNet and configures the system
# for PlebNet.
#

# branch to install from
BRANCH=$1

# expects -testnet, can be extended for more arguments
EXITNODE=$2
TESTNET=$3

CREATECHILD="~/PlebNet/plebnet/clone/create-child.sh"

[ -z $BRANCH ] && BRANCH = "master"

# Add locale
echo 'LANG=en_US.UTF-8' > /etc/locale.conf
locale-gen en_US.UTF-8

# No interactivity
DEBIAN_FRONTEND=noninteractive
echo force-confold >> /etc/dpkg/dpkg.cfg
echo force-confdef >> /etc/dpkg/dpkg.cfg

# Install apt-utils and software-properties-common
apt-get -f -y install
apt install -y software-properties-common

# Add bionic repo
add-apt-repository 'deb http://it.archive.ubuntu.com/ubuntu/ bionic main universe restricted multiverse'
apt update

# Install libtorrent
apt install python3-libtorrent=1.1.5-1build1 -y

# Restoring apt
wget -O /tmp/libc6_2.23-0ubuntu10_amd64.deb http://security.ubuntu.com/ubuntu/pool/main/g/glibc/libc6_2.23-0ubuntu10_amd64.deb
wget -O /tmp/libapt-pkg5.0_1.2.32ubuntu0.1_amd64.deb http://security.ubuntu.com/ubuntu/pool/main/a/apt/libapt-pkg5.0_1.2.32ubuntu0.1_amd64.deb
wget -O /tmp/apt_1.2.32ubuntu0.1_amd64.deb http://security.ubuntu.com/ubuntu/pool/main/a/apt/apt_1.2.32ubuntu0.1_amd64.deb

dpkg -i /tmp/libc6_2.23-0ubuntu10_amd64.deb
dpkg -i /tmp/libapt-pkg5.0_1.2.32ubuntu0.1_amd64.deb
dpkg -i /tmp/apt_1.2.32ubuntu0.1_amd64.deb

apt update
apt-get -f -y install

# Linking python3 to 3.6
rm /usr/local/bin/python3
ln -s /usr/bin/python3.6 /usr/local/bin/python3

# Remove previous pip
apt-get remove --purge -y python-pip python3-pip

# Installing pip
apt install python3-distutils -y
wget -O /tmp/get-pip.py https://bootstrap.pypa.io/get-pip.py
python3 /tmp/get-pip.py

# Clearing temp folder
rm /tmp/*

pip3 install -U wheel setuptools

#(echo "alias pip3='python3 -m pip'" | tee -a ~/.bashrc) && source ~/.bashrc

# Fix paths
echo "fixing paths"
(echo "PATH=$PATH:/usr/local/bin:/usr/bin:/root/.local/bin" | tee -a ~/.bashrc)
(echo "export PATH" | tee -a ~/.bashrc) && source ~/.bashrc

apt-get install -y sshpass

# install openvpn
apt-get install -y openvpn
ln -s "$(which openvpn)" /usr/bin/openvpn

# Install dependencies
apt-get install -y \
    git \
    build-essential \
    libssl-dev \
    swig

pip3 install -U crypto \
    pyasn1 \
    twisted \
    apsw \
    chardet \
    configobj \
    netifaces \
    leveldb \
    decorator \
    feedparser \
    keyring \
    ecdsa \
    pbkdf2 \
    requests \
    dnspython \
    networkx \
    scipy \
    lxml

pip3 install -U six

pip3 install -U protobuf \
    meliae \
    cherrypy \
    M2Crypto \
    jsonrpclib-pelix

pip install -U \
    -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-16.04 \
    wxPython
pip3 install -U pyaes psutil
pip3 install -U pyopenssl

echo "Install Crypto, pynacl, libsodium"
apt-get install -y python3-cryptography \
    python3-nacl \
    python3-libnacl \
    python3-keyrings.alt

# python-socks needed? It's going to be installed by pip later

apt-get install -y libffi-dev software-properties-common
pip3 install -U cryptography \
    pynacl \
    pysocks \
    keyrings.alt \
    libnacl

# add-apt-repository -y ppa:chris-lea/libsodium;
# echo "deb http://ppa.launchpad.net/chris-lea/libsodium/ubuntu trusty main" >> /etc/apt/sources.list;
# echo "deb-src http://ppa.launchpad.net/chris-lea/libsodium/ubuntu trusty main" >> /etc/apt/sources.list;
# apt-get update
apt-get install -y libsodium-dev

# Update pip to avoid locale errors in certain configurations
#echo "upgrading pip"
#LC_ALL=en_US.UTF-8 pip install --upgrade pip
#echo "done upgrading pip"

cd $HOME

KRDIR=~/.local/share/python_keyring/
KRCFG=${KRDIR}keyringrc.cfg
if [ ! -d $KRDIR ]
then    
    mkdir -p $KRDIR
fi

if [ ! -e $KRCFG ]
then 
    touch $KRCFG
    echo "[backend]" >> $KRCFG
    echo "default-keyring=keyrings.alt.file.PlaintextKeyring" >> $KRCFG
fi

[ ! -d "PlebNet" ] && git clone -b $BRANCH https://github.com/GioAc96/Dollynator

mv Dollynator PlebNet

# when branch is given, this create-child.sh's default branch value will be updated
#   this is because the child's cloned repo also needs these values updated
sed -i -E "s/(BRANCH\s*=\s*\")(.+)(\")/\1${BRANCH}\3/" $CREATECHILD && echo "Updated branch to $BRANCH in file ($CREATECHILD)";

pip3 install --upgrade ./PlebNet
cd PlebNet

git submodule init && git submodule update --remote --recursive
cd tribler
git submodule init && git submodule update --remote --recursive
cd ..

# Add paths to internal modules
(echo "export PYTHONPATH=$PYTHONPATH:$HOME/PlebNet/tribler/src/pyipv8:$HOME/PlebNet/tribler/src/anydex:$HOME/PlebNet/tribler/src/tribler-common:$HOME/PlebNet/tribler/src/tribler-core:$HOME/PlebNet/tribler/src/tribler-gui" | tee -a ~/.bashrc) && source ~/.bashrc

# Install Firefox for cloudomate
apt-get install -y firefox

pip3 install ./cloudomate

# Install tribler
pip3 install pony
pip3 install -r ./tribler/src/requirements.txt
cd ..

# Install bitcoinlib
# pip install bitcoinlib==0.4.4
apt-get install -y libgmp-dev
git clone https://github.com/1200wd/bitcoinlib.git
pip3 install ./bitcoinlib

# Install electrum as it is required by cloudomate and not included in tribler anymore
# git clone -b 2.9.x https://github.com/spesmilo/electrum.git
# cd electrum
# python3 setup.py install
# sudo apt-get -y install protobuf-compiler
# protoc --proto_path=lib/ --python_out=lib/ lib/paymentrequest.proto
apt-get install -y python3-pyqt5
wget https://download.electrum.org/3.3.8/Electrum-3.3.8.tar.gz
pip3 install Electrum-3.3.8.tar.gz[fast]

cd /root

ARGS=""
[[ $EXITNODE -eq 1 ]] && ARGS="--exitnode";
[[ $TESTNET -eq 1 ]] && ARGS="${ARGS} --testnet";

echo "arguments: $ARGS"

if [[ $TESTNET -eq 1 ]]; then
    plebnet setup $ARGS >> plebnet.log 2>&1
    echo "Installed in testnet mode: TBTC bitcoin wallet used, no cron job checking - run \"plebnet check\" manually."
else
    plebnet setup $ARGS >> plebnet.log 2>&1
    echo "*/5 * * * * root /usr/local/bin/plebnet check >> plebnet.log 2>&1" > /etc/cron.d/plebnet
    echo "Installed in normal mode: BTC bitcoin wallet used, cron job created, exit node is on"
fi
