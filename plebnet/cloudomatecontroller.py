# -*- coding: utf-8 -*-
import ConfigParser
import codecs
import random
import unicodedata

import cloudomate
from appdirs import user_config_dir
from cloudomate import wallet as wallet_util
from cloudomate.cmdline import providers as cloudomate_providers
from cloudomate.util.config import UserOptions, os
from faker.factory import Factory


def status(provider):
    settings = _user_settings()
    return provider.get_status(settings)


def get_ip(provider):
    settings = _user_settings()
    return provider.get_ip(settings)


def estimate_price(provider, option):
    """
    Estimate the price for purchasing option at provider
    :param provider: 
    :param option
    :return: 
    """
    cl_provider = cloudomate_providers[provider]
    vpsoption = cl_provider.options()[option]
    gateway = cl_provider.gateway
    btc_price = gateway.estimate_price(cloudomate.wallet.get_price(vpsoption.price, vpsoption.currency)) \
                + cloudomate.wallet.get_network_fee()
    return btc_price


def setrootpw(provider, password):
    """
    Reset root password for server hosted at provider
    :param provider: 
    :param password: 
    :return: 
    """
    cl_provider = cloudomate_providers[provider]
    settings = _user_settings()
    settings.put('rootpw', password)
    return cl_provider.set_rootpw(settings)


def options(provider):
    """
    Return the vps options for provider
    :param provider: 
    :return: 
    """
    return cloudomate_providers[provider].options()


def purchase(provider, vps_option, wallet):
    """
    Purchace the chosen vps_option from provider with funds in wallet
    :param provider: 
    :param vps_option: 
    :param wallet: 
    :return: 
    """
    settings = _user_settings()
    option = options(provider)[vps_option]
    try:
        transaction_hash = provider.purchase(settings, option, wallet)
        print("Transaction hash of purchase: {0}".format(transaction_hash))
        return transaction_hash
    except SystemExit, e:
        print("SystemExit catched at cloudomatecontroller purchase")
        print(e)
        return False


def generate_config():
    """
    Generate a new identity for the newly installed child
    :return: 
    """
    config = UserOptions()
    filename = os.path.join(user_config_dir(), 'cloudomate.cfg')
    if os.path.exists(filename):
        print("cloudomate.cfg already present at %s" % filename)
        config.read_settings(filename=filename)
        return config
    locale = random.choice(['cs_CZ', 'de_DE', 'dk_DK', 'es_ES', 'et_EE', 'hr_HR', 'it_IT'])
    fake = Factory().create(locale)
    cp = ConfigParser.ConfigParser()
    _generate_address(cp, fake)
    _generate_server(cp, fake)
    _generate_user(cp, fake)
    _remove_unicode(cp)
    with codecs.open(filename, 'w', 'utf8') as config_file:
        cp.write(config_file)
    return cp


def _remove_unicode(cp):
    """
    Remove unicode to avoid errors in python2
    :param cp: 
    :return: 
    """
    for section in cp.sections():
        for option in cp.options(section):
            item = cp.get(section, option)
            if isinstance(item, unicode):
                cp.set(section, option, unicodedata.normalize('NFKD', item).encode('ascii', 'ignore'))


def _generate_user(cp, fake):
    cp.add_section('User')
    firstname = fake.first_name()
    lastname = fake.last_name()
    full_name = firstname + '_' + lastname
    full_name = full_name.replace(' ', '_')
    cp.set('User', 'email', full_name + '@heijligers.me')
    cp.set('User', 'firstname', firstname)
    cp.set('User', 'lastname', lastname)
    cp.set('User', 'companyname', fake.company())
    cp.set('User', 'phonenumber', fake.numerify('##########'))
    cp.set('User', 'password', fake.password(length=10, special_chars=False))


def _generate_address(cp, fake):
    cp.add_section('Address')
    cp.set('Address', 'address', fake.street_address())
    cp.set('Address', 'city', fake.city())
    cp.set('Address', 'state', fake.state())
    cp.set('Address', 'countrycode', fake.country_code())
    cp.set('Address', 'zipcode', fake.postcode())


def _generate_server(cp, fake):
    cp.add_section('Server')
    cp.set('Server', 'rootpw', fake.password(length=10, special_chars=False))
    cp.set('Server', 'ns1', 'ns1')
    cp.set('Server', 'ns2', 'ns2')
    cp.set('Server', 'hostname', fake.word())


def _user_settings():
    """
    Load the default user config.
    :return: 
    """
    settings = UserOptions()
    settings.read_settings()
    return settings


def reset_browser(provider):
    """
    Reset browser to start with a new stateless browser.
    :param provider: 
    :return: 
    """
    cl_provider = cloudomate_providers[provider]
    cl_provider.br = cl_provider._create_browser()
