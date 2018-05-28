#!/usr/bin/env bash

#
# This file is used to create a new PlebNet agent on a remote server.
#
# It should be called with two parameters:
#  1: The ip address of the remote server
#  2: the root password of the remote server
#
# It creates a connection, copies the agent specific files (DNA) and
# pulls the latest version of PlebNet from a Git repo. Then it runs
# the installation script provided by the latests version.
#

IP=$1
PASSWORD=$2
CHILD_DNA_FILE="~/.config/Child_DNA.json"
DNA_FILE="~/.config/DNA.json"
WALLET_FILE="~/.electrum/wallets/default_wallet"

export DEBIAN_FRONTEND=noninteractive

cd

[ -z "$1" ] || [ -z "$2" ] && echo "Usage: $0 <ip address> <password>" && exit 1

if ! hash sshpass 2> /dev/null; then
    echo "Installing sshpass"
    apt-get install -y sshpass
fi

echo "Creating directories"
sshpass -p${PASSWORD} ssh  -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@${IP} 'mkdir -p data/; mkdir -p .config/; mkdir -p .electrum/wallets/; mkdir -p .Tribler/wallet/'

echo "Copying DNA"
if [ ! -e ${CHILD_DNA_FILE} ]; then
    echo "File $CHILD_DNA_FILE not found"
else
    sshpass -p${PASSWORD} scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no ${CHILD_DNA_FILE} root@${IP}:${DNA_FILE}
fi

echo "Symlinking to Tribler wallet"
sshpass -p${PASSWORD} ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@${IP} "ln -s ~/${WALLET_FILE} .Tribler/wallet/btc_wallet"

echo "install openssl"
sshpass -p${PASSWORD} ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@${IP} 'apt-get update && \
    apt-get install -y openssl && \
    apt-get install -y ca-certificates'

echo "Installing PlebNet"
sshpass -p${PASSWORD} ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@${IP} 'apt-get install -y git && \
    git clone -b update_install_scripts https://github.com/vwigmore/PlebNet && \
    cd PlebNet && sh plebnet/clone/install.sh'
