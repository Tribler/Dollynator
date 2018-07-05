"""
This file contains all code used to setup a new PlebNet agent on a remote server.

It used the available servers listed in the configuration and tries to install
the latest version of PlebNet on these servers.
"""

import os
import time
import subprocess

from plebnet.controllers import cloudomate_controller
from plebnet.settings import plebnet_settings as setup
from plebnet.utilities import logger


def install_available_servers(config, dna):
    """
    This function checks if any of the bought servers are ready to be installed and installs
    PlebNet on them.
    :param config: The configuration of this Plebbot
    :type config: dict
    :param dna: The DNA of this Plebbot
    :type dna: DNA
    :return: None
    :rtype: None
    """
    bought = config.get('bought')
    logger.log("install: %s" % bought, "install_available_servers")

    for provider, transaction_hash, child_index in list(bought):

        # skip vpn providers as they show up as 'bought' as well
        if provider in cloudomate_controller.get_vpn_providers():
            return

        try:
            provider_class = cloudomate_controller.get_vps_providers()[provider]
            ip = cloudomate_controller.get_ip(provider_class, cloudomate_controller.child_account(child_index))
        except Exception as e:
            logger.log(str(e) + "%s not ready yet" % str(provider), "install_available_servers")
            return
            
        if is_valid_ip(ip):

            # VPN configuration, enable tun/tap settings
            if provider_class.TUN_TAP_SETTINGS:
                tun_success = provider_class(cloudomate_controller.child_account(child_index)).enable_tun_tap()
                logger.log("Enabling %s tun/tap: %s"%(provider, tun_success))
                if not cloudomate_controller.save_info_vpn(child_index):
                    logger.log("VPN not ready yet, can't save ovpn config")
                    return

            logger.log("Installing child on %s with ip %s" % (provider, str(ip)))

            account_settings = cloudomate_controller.child_account(child_index)
            rootpw = account_settings.get('server', 'root_password')

            provider_class(cloudomate_controller.child_account(child_index)).change_root_password(rootpw)
            time.sleep(5)

            child_tree = dna.get_own_tree() + '.' + str(child_index)

            dna.create_child_dna(provider, child_tree, transaction_hash)

            # Save config before entering possibly long lasting process
            config.save()

            success = _install_server(ip, rootpw, child_index, setup.get_instance().wallets_testnet())

            # Reload config in case install takes a long time
            config.load()
            config.get('installed').append({provider: success})
            if [provider, transaction_hash, child_index] in config.get('bought'):
                config.get('bought').remove([provider, transaction_hash, child_index])
            config.save()
        else:
            logger.log("Server not ready")


def is_valid_ip(ip):
    """
    This methods checks if the provided ip-address is valid.
    :param ip: The ipadress to check
    :type ip: String
    :return: True/False
    :rtype: Boolean
    """
    if ip:
        pieces = ip.strip().split('.')
        if len(pieces) != 4:
            return False
        try:
            if 0 <= int(pieces[1]) < 256:
                return all(0 <= int(p) < 256 for p in pieces)
        except ValueError:
            return False
    return False


def check_access(ip, rootpw):
    check = subprocess.call(['sshpass', '-p', rootpw, 'ssh',
                             '-o', 'UserKnownHostsFile=/dev/null',
                             '-o', 'StrictHostKeyChecking=no', 'root@'+ip,
                             'exit'])
    return is_valid_ip(ip) and check == 0


def _install_server(ip, rootpw, vpn_child_index=None, testnet=False):
    """
    This function starts the actual installation routine.
    :param ip: The ip-address of the remote server
    :type ip: String
    :param rootpw: The root password of the remote server
    :type rootpw: String
    :return: The exit status of the installation
    :rtype: Integer
    """
    settings = setup.get_instance()
    home = settings.plebnet_home()
    script_path = os.path.join(home, "plebnet/clone/create-child.sh")
    logger.log('tot_path: %s' % script_path)

    command = ["bash", script_path, "-i", ip.strip(), "-p", rootpw.strip()]

    # additional VPN arguments
    if vpn_child_index > -1:
        prefix = settings.vpn_child_prefix()

        dir = os.path.expanduser(settings.vpn_config_path())
        
        # vpn credentials: ~/child_INT_credentials.conf
        credentials = os.path.join(dir, prefix + str(vpn_child_index) + settings.vpn_credentials_name())
        # vpn credentials destination: own_config.ovpn
        dest_credentials = settings.vpn_own_prefix() + settings.vpn_credentials_name()

        # vpn config: ~/child_INT_config.ovpn
        ovpn = os.path.join(dir, prefix + str(vpn_child_index) + settings.vpn_config_name())
        # vpn config destination: own_credentials.conf
        dest_config = settings.vpn_own_prefix() + settings.vpn_config_name()

        # the current child config is given as arguments, the destination is so that the
        # agent knows it's its own configuration, and not a child's config.
        command += ["-conf", ovpn, dest_config, "-cred", credentials, dest_credentials]

    if testnet:
        command.append("-t")

    if settings.tribler_exitnode():
        command.append("-e")

    logger.log("Running %s" % ' '.join(command), '_install_server')
    exitcode = subprocess.call(command, cwd=home)
    if exitcode == 0:
        logger.log("Installation successful")
        return True
    else:
        logger.log("Installation unsuccessful, error code: %s" % exitcode)
        return False
