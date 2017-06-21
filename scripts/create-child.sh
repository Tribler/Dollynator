#!/bin/bash
IP=$1
PASSWORD=$2

apt-get install -y sshpass

echo "sshpass -p$PASSWORD ssh root@$IP echo hi"
sshpass -p$PASSWORD ssh root@$IP
