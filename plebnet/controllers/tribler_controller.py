"""
This file is used to control all dependencies with Tribler.

Other files should never have a direct import from Tribler, as the reduces the maintainability of this code.
If Tribler alters its call methods, this should be the only file which needs to be updated in PlebNet.
"""

import os
import subprocess

from plebnet.utilities import logger
from plebnet.settings import plebnet_settings
from plebnet.controllers import market_controller

setup = plebnet_settings.get_instance()

def running():
    """
    Check if tribler is running.
    :return: True if twistd.pid exists in /root/tribler
    """

    # TODO: kijken of het proces draait ipv het bestand aanwezig is
    path = os.path.join(setup.tribler_home(), setup.tribler_pid())
    return os.path.isfile(path)


def start():
    """
    Start tribler
    :return:
    """
    env = os.environ.copy()
    env['PYTHONPATH'] = setup.tribler_home()
    try:
        success = subprocess.call(['twistd', '--pidfile='+setup.tribler_pid(),
                                   'plebnet', '-p', '8085', '--exitnode'],
                                  cwd=setup.tribler_home(), env=env)
        if not success:
            logger.error('Failed to start Tribler', "tribler_controller")
            return False
        logger.success('Tribler is started', "tribler_controller")

        logger.log('market running: ' + str(market_controller.is_market_running()))
        return True
    except subprocess.CalledProcessError as e:
        logger.error(e.output, "Tribler starter", "tribler_controller")
        return False
