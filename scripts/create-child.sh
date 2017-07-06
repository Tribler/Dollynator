#!/usr/bin/env bash
IP=$1
PASSWORD=$2
CHILD_DNA_FILE=".config/Child_DNA.json"
DNA_FILE=".config/DNA.json"
WALLET_FILE=".electrum/wallets/default_wallet"
TWITTER_FILE=".config/twitter.cfg"

export DEBIAN_FRONTEND=noninteractive

cd

[ -z "$1" ] || [ -z "$2" ] && echo "Usage: $0 <ip address> <password>" && exit 1

if ! hash sshpass 2> /dev/null; then
    echo "Installing sshpass"
    apt-get install -y sshpass
fi

echo "Creating directories"
sshpass -p${PASSWORD} ssh -o StrictHostKeyChecking=no root@${IP} 'mkdir -p .config/; mkdir -p .electrum/wallets/; mkdir -p .Tribler/wallet/'

echo "Copying DNA"
[ ! -f ${CHILD_DNA_FILE} ] && echo "File $CHILD_DNA_FILE not found" && exit 1
sshpass -p${PASSWORD} scp -o StrictHostKeyChecking=no ${CHILD_DNA_FILE} root@${IP}:${DNA_FILE}

#echo "Copying wallet"
#[ ! -f ${WALLET_FILE} ] && echo "File $WALLET_FILE not found" && exit 1
#sshpass -p${PASSWORD} scp -o StrictHostKeyChecking=no ${WALLET_FILE} root@${IP}:${WALLET_FILE}

echo "Copying Twitter auth"
[ ! -f ${TWITTER_FILE} ] && echo "File $TWITTER_FILE not found" && exit 1
sshpass -p${PASSWORD} scp -o StrictHostKeyChecking=no ${TWITTER_FILE} root@${IP}:${TWITTER_FILE}

echo "Symlinking to Tribler wallet"
sshpass -p${PASSWORD} ssh -o StrictHostKeyChecking=no root@${IP} "ln -s ~/${WALLET_FILE} .Tribler/wallet/btc_wallet"


echo "Installing PlebNet"
sshpass -p${PASSWORD} ssh -o StrictHostKeyChecking=no root@${IP} 'apt-get update && \
    apt-get install -y git && \
    git clone -b master https://github.com/rjwvandenberg/PlebNet && \
    cd PlebNet && scripts/install.sh'
