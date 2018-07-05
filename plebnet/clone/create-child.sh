#!/usr/bin/env bash

#
# This file is used to create a new PlebNet agent on a remote server.
#
#    Usage: ./create-child.sh <parameter> <value>
#    -h --help 		 Shows this help message
#    -i --ip 		 Ip address of the server to run install on
#    -p --password 		 Root password of the server
#    -t --testnet 		 Install agent in testnet mode (default 0)
#    -e --exitnode       Run as exitnode for Tribler
#    -conf --config 		 (optional) VPN configuration file (.ovpn)
#    -cred --credentials 	 (optional) VPN credentials file (.conf)
#

# It creates a connection, copies the agent specific files (DNA) and
# pulls the latest version of PlebNet from a Git repo. Then it runs
# the installation script provided by the latests version.
#

OWN="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/create-child.sh"

CHILD_DNA_FILE=~/.config/Child_DNA.json
DNA_FILE=~/.config/DNA.json
# WALLET_FILE="~/.electrum/wallets/default_wallet"

export DEBIAN_FRONTEND=noninteractive

cd

CHILD_DNA_FILE=~/.config/Child_DNA.json
DNA_FILE=~/.config/DNA.json
WALLET_FILE=~/.electrum/wallets/default_wallet
TESTNET_WALLET_FILE=~/.electrum/testnet/wallets/default_wallet

IP=""
PASSWORD=""
VPN_CONFIG=""
VPN_CREDENTIALS=""
DEST_VPN_CONFIG=""
DEST_VPN_CREDENTIALS=""
BRANCH="master"
TESTNET=0
EXITNODE=0

############################### PARSING ########################################
function usage()
{
    printf "
Usage: ./create-child.sh <parameter> <value>
-h --help \t\t Shows this help message
-i --ip \t\t Ip address of the server to run install on
-p --password \t\t Root password of the server
-t --testnet \t\t Install agent in testnet mode (default 0)
-e --exitnode \t\t Run as exitnode for tribler
-conf --config \t\t (optional) VPN configuration file (.ovpn)
Requires the destination config name.
Example: -conf source_config.ovpn dest_config.ovpn

-cred --credentials \t (optional) VPN credentials file (.conf)
Requires the destination credentials name.
Example -cred source_credentials.conf dest_credentials.conf

-b --branch \t\t (optional) Branch of code to install from (default master)
\n
"
}

while [ "$1" != "" ]; do
	PARAM=$1
	VALUE=$2
	MORE=$3

	case $PARAM in
		-h | --help)
			usage
			exit
			;;
		-i | --ip)
			IP=$VALUE
			shift
			shift
			;;
		-p | --password)
			PASSWORD=$VALUE
			shift
			shift
			;;
		-conf | --config)
			VPN_CONFIG=$VALUE
			DEST_VPN_CONFIG=$MORE
			[ -z $VALUE ] && echo "ERROR: provide VPN config (.ovpn)" && usage && exit;
			[ -z $MORE ] && echo "ERROR: provide VPN config destination name (.ovpn)" && usage && exit;
			shift
			shift
			shift
			;;
		-cred | --credentials)
			VPN_CREDENTIALS=$VALUE
			DEST_VPN_CREDENTIALS=$MORE
			[ -z $VALUE ] && echo "ERROR: provide VPN credentials (.conf)" && usage && exit;
			[ -z $MORE ] && echo "ERROR: provide VPN credentials destination name (.ovpn)" && usage && exit;
			shift
			shift
			shift
			;;
		-t | --testnet)
			TESTNET=1
			shift
			;;
		-e | --exitnode)
			EXITNODE=1
			shift
			;;
		-b | --branch)
		    BRANCH=$VALUE
		    [ -z $VALUE ] && echo "ERROR: provide branch" && usage && exit;
		    # when branch is given, this file's default branch value will be updated
		    #   install.sh does the same for its default branch value, including this file
		    #   this is because the child's cloned repo also needs these values updated
		    sed -i -E "s/(BRANCH\s*=\s*\")(.+)(\")/\1${BRANCH}\3/" $OWN && echo "Updated branch to $BRANCH in this file ($OWN)";
		    shift
		    shift
		    ;;
		*)
			echo "ERROR: invalid parameter \"$PARAM\""
			usage
			exit 1
			;;
	esac
done

[ -z $IP ] || [ -z $PASSWORD ] && echo "ERROR: provide valid IP and root password" && usage && exit 1;

# if testnet (-t) is set, install.sh is called with additional "-test" argument
if [[ $TESTNET -eq 1 ]]; then
	echo "(testnet is ON)";
else
	echo "(testnet is OFF)";
fi

# if exitnode (-e) is set, install.sh is called with additional "--exitnode" argument
if [[ $EXITNODE -eq 1 ]]; then
	echo "(exitnode is ON)";
else
    echo "(exitnode is OFF)";
fi

############################### INSTALL REQUIREMENTS ########################################

echo "Installing sshpass"
apt-get install -y sshpass


echo "install openssl"
sshpass -p${PASSWORD} ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@${IP} 'apt-get update && \
    apt-get install -y openssl && \
    apt-get install -y ca-certificates'

############################### SERVER DIRECTORIES SETUP ########################################
echo "Creating directories"
sshpass -p${PASSWORD} ssh  -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@${IP} 'mkdir -p .config/; mkdir -p .electrum/wallets/; mkdir -p .Tribler/wallet/'

############################### COPYING FILES ########################################
echo "Copying DNA"
if [ ! -e ${CHILD_DNA_FILE} ]; then
    echo "File $CHILD_DNA_FILE not found"
else
    sshpass -p${PASSWORD} scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no ${CHILD_DNA_FILE} root@${IP}:${DNA_FILE}
fi

# copying VPN configs if they exist
if [[ $VPN_CONFIG == "" ]] || [[ $VPN_CREDENTIALS == "" ]]; then
	echo "(no VPN configs given)";
else
    echo "copying VPN configs to child's ~/"
    sshpass -p${PASSWORD} scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no ${VPN_CONFIG} root@${IP}:~/${DEST_VPN_CONFIG};
    sshpass -p${PASSWORD} scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no ${VPN_CREDENTIALS} root@${IP}:~/${DEST_VPN_CREDENTIALS};
fi

# Symlinking Tribler wallet to the default electrum wallet, might be usable for other purposes later.
# echo "Symlinking to Tribler wallet"
#sshpass -p${PASSWORD} ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@${IP} "ln -s .Tribler/wallet/btc_wallet ${WALLET_FILE}"
#sshpass -p${PASSWORD} ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@${IP} "ln -s .Tribler/wallet/tbtc_wallet ${TESTNET_WALLET_FILE}"

############################### INSTALL PLEBNET AND SUBMODULES ########################################
echo "Installing PlebNet"
echo "Installing from branch: $BRANCH";

sshpass -p${PASSWORD} ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@${IP} "wget https://raw.githubusercontent.com/vwigmore/plebnet/$BRANCH/plebnet/clone/install.sh && \
    chmod +x install.sh && \
    ./install.sh $BRANCH $EXITNODE $TESTNET | tee plebnet_installation.log"
