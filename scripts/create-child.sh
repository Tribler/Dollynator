#!/bin/bash
IP=$1
PASSWORD=$2
DNA_FILE=".config/DNA.json"
WALLET_FILE=".electrum/wallets/default_wallet"

[ -z "$1" ] || [ -z "$2" ] && echo "Usage: $0 <ip address> <password>" && exit 1

if ! hash sshpass 2> /dev/null; then
    echo "Installing sshpass"
    apt-get install -y sshpass
fi

echo "Creating directories"
sshpass -p$PASSWORD ssh root@$IP 'mkdir -p .config/; mkdir -p .electrum/wallets/'


echo "Copying DNA"
[ ! -f $HOME/$DNA_FILE ] && echo "File $HOME/$DNA_FILE not found" && exit 1
sshpass -p$PASSWORD scp $HOME/$DNA_FILE root@$IP:$DNA_FILE

echo "Copying wallet"
[ ! -f $HOME/$WALLET_FILE ] && echo "File $HOME/$WALLET_FILE not found" && exit 1
sshpass -p$PASSWORD scp $HOME/$WALLET_FILE root@$IP:$WALLET_FILE

echo "Installing PlebNet"
sshpass -p$PASSWORD ssh root@$IP 'apt-get update && \
    apt-get install git && \
    git clone https://github.com/rjwvandenberg/PlebNet && \
    cd PlebNet && git checkout scripts && scripts/install.sh'
