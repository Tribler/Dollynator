#!/bin/bash

# Quickly resetting a server/container by removing configuration folders
# and uninstalling PlebNet and cloudomate

echo "killing tribler, plebnet"
for pid in $(ps aux | grep -E 'twistd|plebnet|openvpn' | awk '{print $2}'); do kill -9 $pid; done

declare -a files=(~/.Tribler
                    ~/.config
                    ~/PlebNet
                    ~/cloudomate
                    ~/plebnet*
                    ~/get-pip.py
                    ~/install.sh
                    ~/.local/share/python_keyring/keyring_pass.cfg
                    )

for item in "${files[@]}"
do 
    echo "removing ${item}" && rm -rf "${item}"
done


echo "uninstalling plebnet" && pip uninstall -y plebnet 
echo "uninstalling cloudomate" && pip uninstall -y cloudomate 

mkdir -p ~/.config/

