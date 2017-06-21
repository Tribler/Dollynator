#!/bin/bash
IP=$1
PASSWORD=$2

apt-get install -y sshpass

echo "sshpass -p$PASSWORD ssh root@$IP echo hi"
sshpass -p$PASSWORD ssh root@$IP 'apt-get update && \
    apt-get install git && \
    git clone https://github.com/rjwvandenberg/PlebNet && \
    cd PlebNet && git checkout scripts && scripts/install.sh'
