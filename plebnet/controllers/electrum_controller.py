"""
This file is used to control all dependencies with Electrum.

Other files should never have a direct import from Electrum, as the reduces the maintainability of this code.
If Electrum alters its call methods, this should be the only file which needs to be updated in PlebNet.
"""

import os
import electrum

from electrum import Wallet as ElectrumWallet
from electrum import WalletStorage
from electrum import keystore
from electrum.mnemonic import Mnemonic

from plebnet.utilities import logger

WALLET_FILE = os.path.expanduser("~/.electrum/wallets/default_wallet")


def create_wallet():
    """
    Create an electrum wallet if it does not exist
    :return:
    """
    if not os.path.isfile(WALLET_FILE):
        logger.log("Creating wallet", "create_wallet")
        config = electrum.SimpleConfig()
        storage = WalletStorage(config.get_wallet_path())
        passphrase = config.get('passphrase', '')
        seed = Mnemonic('en').make_seed()
        k = keystore.from_seed(seed, passphrase)
        k.update_password(None, None)
        storage.put('keystore', k.dump())
        storage.put('wallet_type', 'standard')
        storage.put('use_encryption', False)
        storage.write()
        wallet = ElectrumWallet(storage)
        wallet.synchronize()
        logger.log("Your wallet generation seed is:\n\"%s\"" % seed, "create_wallet")
        logger.log("Please keep it in a safe place; once lost, your wallet cannot be restored.", "create_wallet")
        wallet.storage.write()
        logger.log("Wallet saved in '%s'" % wallet.storage.path, "create_wallet")
    else:
        logger.log("Wallet already present", "create_wallet")

