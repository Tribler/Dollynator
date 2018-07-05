# -*- coding: utf-8 -*-

"""
This file is used to control all dependencies with Cloudomate.

Other files should never have a direct import from Cloudomate, as this reduces the maintainability
of this code. If Cloudomate alters its call methods, this should be the only file which needs
to be updated in PlebNet.
"""

import io
import os
import sys
import traceback

from os import path
from appdirs import user_config_dir

from cloudomate import wallet as wallet_util
from cloudomate.cmdline import providers as cloudomate_providers
from cloudomate.hoster.vps.clientarea import ClientArea
from cloudomate.util.settings import Settings as AccountSettings
from cloudomate.hoster.vps.proxhost import ProxHost

from plebnet.agent.config import PlebNetConfig
from plebnet.controllers import market_controller
from plebnet.controllers.wallet_controller import TriblerWallet
from plebnet.settings import plebnet_settings
from plebnet.utilities import logger
from plebnet.agent.dna import DNA
from plebnet.communication import git_issuer


def get_vps_providers():
    """
    This method returns the list of VPS providers available in Cloudomate.
    :return: list of VPS providers
    """
    return cloudomate_providers['vps']


def get_vpn_providers():
    return cloudomate_providers['vpn']


def child_account(index=None):
    """
    This method returns the configuration for a certain child number.
    :param index: The number of the child
    :type index: Integer
    :return: configuration of the child
    :rtype: Settings
    """
    if index > -1:
        account = AccountSettings()
        account.read_settings(
            os.path.join(user_config_dir(), 'child_config' + str(index) + '.cfg'))
    else:
        account = AccountSettings()
        account.read_settings(
            os.path.join(user_config_dir(), 'child_config' + str(PlebNetConfig().get("child_index")) + '.cfg'))
    return account


def status(provider):
    """
    This method returns the status parameters of a provider as specified in Cloudomate.
    :param provider: The provider to check
    :type provider: dict
    :return: status
    :rtype: String
    """
    account = child_account()
    return provider.get_status(account)


def get_ip(provider, account):
    """
    This method returns the IP address of the specified provider and account.
    :param provider: The provider
    :param account: the account information
    :return: IP address
    """
    logger.log('get ip: %s' % provider)
    if provider == ProxHost:
        provider_instance = provider(account)
        ip = provider_instance.get_configuration().ip
        return ip
    else:
        client_area = ClientArea(provider._create_browser(), provider.get_clientarea_url(), account)
        logger.log('client area: %s' % client_area.get_services())
        return client_area.get_ip()


def setrootpw(provider, password):
    settings = child_account()
    settings.put('server', 'root_password', password)
    return # provider.set_rootpw(settings)


def options(provider):
    return provider.get_options()


def get_network_fee():
    return wallet_util.get_network_fee()


def pick_provider(providers):
    """
    This method picks a provider based on the DNA o the agent.
    :param providers:
    :return:
    """
    provider = DNA.choose_provider(providers)
    gateway = get_vps_providers()[provider].get_gateway()
    option, price, currency = pick_option(provider)
    btc_price = gateway.estimate_price(
        wallet_util.get_price(price, currency))
    return provider, option, btc_price


def pick_option(provider):
    """
    Pick most favorable option at a provider. For now pick the cheapest option.
    :param provider: The chosen provider
    :return: (option, price, currency)
    """
    vps_options = options(cloudomate_providers['vps'][provider])
    if len(vps_options) == 0:
        return

    cheapest_option = 0
    for item in range(len(vps_options)):
        if vps_options[item].price < vps_options[cheapest_option].price:
            cheapest_option = item

    logger.log("cheapest option: %s" % str(vps_options[cheapest_option]))
    return cheapest_option, vps_options[cheapest_option].price, 'USD'


def update_offer(config):
    """
    Retrieve the price of the chosen server to buy and make a new offer on the Tribler marketplace.
    :param config: configuration of the agent
    :return: None
    """
    if not config.get('chosen_provider'):
        return
    (provider, option, _) = config.get('chosen_provider')
    btc_price = calculate_price(provider, option) * 1.15
    place_offer(btc_price, config)


def calculate_price(provider, option):
    """
    Calculate the price of the chosen server to buy.
    :param provider: the provider chosen
    :param option: the option at the provider chosen
    :return: the price
    """
    logger.log('provider: %s option: %s' % (provider, option), "cloudomate_controller")
    vps_option = options(cloudomate_providers['vps'][provider])[option]
    gateway = cloudomate_providers['vps'][provider].get_gateway()
    btc_price = gateway.estimate_price(
        wallet_util.get_price(vps_option.price, 'USD'))
    return btc_price


def calculate_price_vpn(vpn_provider='azirevpn'):
    logger.log('vpn provider: %s' % vpn_provider, "cloudomate_controller")
    # option is assumed to be the first one
    vpn_option = options(get_vpn_providers()[vpn_provider])[0]
    gateway = get_vpn_providers()[vpn_provider].get_gateway()
    btc_price = gateway.estimate_price(
        wallet_util.get_price(vpn_option.price, 'EUR'))
    return btc_price


def purchase_choice_vpn(config):
    provider = plebnet_settings.get_instance().vpn_host()

    provider_instance = get_vpn_providers()[provider](child_account())

    # no need to generate new child config

    wallet = TriblerWallet(plebnet_settings.get_instance().wallets_testnet_created())
    c = cloudomate_providers['vpn'][provider]

    configurations = c.get_options()
    # option is assumbed to be the first vpn provider option
    option = configurations[0]

    transaction_hash = provider_instance.purchase(wallet, option)

    if not transaction_hash:
        logger.warning("Failed to purchase vpn")
        return plebnet_settings.FAILURE
    if False:
        logger.warning("Insufficient funds to purchase server")
        return plebnet_settings.UNKNOWN

    config.get('bought').append((provider, transaction_hash, config.get('child_index')))
    config.get('transactions').append(transaction_hash)
    config.save()

    return plebnet_settings.SUCCESS


def purchase_choice(config):
    """
    Purchase the cheapest provider in chosen_providers. If buying is successful this provider is
    moved to bought. In any case the provider is removed from choices.
    :param config: config
    :return: plebnet_settings errorcode
    """

    (provider, option, _) = config.get('chosen_provider')
    provider_instance = cloudomate_providers['vps'][provider](child_account())

    wallet = TriblerWallet(plebnet_settings.get_instance().wallets_testnet_created())
    c = cloudomate_providers['vps'][provider]

    configurations = c.get_options()
    option = configurations[option]

    try:
        transaction_hash = provider_instance.purchase(wallet, option)
    except:
        title = "Failed to purchase server: %s" % sys.exc_info()[0]
        body = traceback.format_exc()
        logger.error(title)
        logger.error(body)
        git_issuer.handle_error(title, body)
        git_issuer.handle_error("Failed to purchase server", sys.exc_info()[0], ['crash'])
        return plebnet_settings.FAILURE

    if not transaction_hash:
        return plebnet_settings.FAILURE
    config.get('bought').append((provider, transaction_hash, config.get('child_index')))
    config.get('transactions').append(transaction_hash)
    config.set('chosen_provider', None)
    config.save()

    return plebnet_settings.SUCCESS


def place_offer(chosen_est_price, config):
    """
    Sell all available MB for the chosen estimated price on the Tribler market.
    :param config: config
    :param chosen_est_price: Target amount of BTC to receive
    :return: success of offer placement
    """
    available_mb = market_controller.get_balance('MB')
    if available_mb == 0:
        logger.log("No MB available")
        return False
    config.bump_offer_date()

    coin = 'TBTC' if plebnet_settings.get_instance().wallets_testnet() else 'BTC'

    config.set('last_offer', {coin: chosen_est_price, 'MB': available_mb})
    price_per_unit = max(0.0001, chosen_est_price / float(available_mb))
    return market_controller.put_ask(price=price_per_unit,
                                     price_type=coin,
                                     quantity=available_mb,
                                     quantity_type='MB',
                                     timeout=plebnet_settings.TIME_IN_HOUR)


def save_info_vpn(child_index):
    """
    Stores the child vpn information
    :param location: where to store the config
    :return:
    """
    vpn = get_vpn_providers()[plebnet_settings.get_instance().vpn_host()](child_account())
    info = vpn.get_configuration()
    prefix = plebnet_settings.get_instance().vpn_child_prefix()


    dir = path.expanduser(plebnet_settings.get_instance().vpn_config_path())
    credentials = prefix + str(child_index) +plebnet_settings.get_instance().vpn_credentials_name()
        
    ovpn = prefix + str(child_index) +plebnet_settings.get_instance().vpn_config_name()

    # the .ovpn file contains the line auth-user-pass so that it knows which credentials file to use
    # when the child config and credentials are passed to create-child, it is placed on the server as "own" 
    # so the reference to "own" is put in the .ovpn file.
    own_credentials = plebnet_settings.get_instance().vpn_own_prefix() \
                      + plebnet_settings.get_instance().vpn_credentials_name()
    with io.open(path.join(dir, ovpn), 'w', encoding='utf-8') as ovpn_file:
        ovpn_file.write(info.ovpn + '\nauth-user-pass ' + own_credentials)

    # write the ovpn file to vpn dir
    with io.open(path.join(dir, credentials), 'w', encoding='utf-8') as credentials_file:
        credentials_file.writelines([info.username + '\n', info.password])

    print("Saved VPN configuration to " + dir)

    return True
