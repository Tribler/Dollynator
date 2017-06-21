#!/bin/bash
IP=$1
PASSWORD=$2

[ -z "$1" ] || [ -z "$2" ] && echo "Usage: $0 <ip address> <password>" && exit 1

if ! hash sshpass 2> /dev/null; then
    apt-get install -y sshpass
fi

sshpass -p$PASSWORD ssh root@$IP 'apt-get update && \
    apt-get install git && \
    git clone https://github.com/rjwvandenberg/PlebNet && \
    cd PlebNet && git checkout scripts && scripts/install.sh'
