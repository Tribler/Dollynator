# -*- coding: utf-8 -*-
import ConfigParser
import codecs
import random
import unicodedata

from appdirs import user_config_dir
from cloudomate import wallet as wallet_util
from cloudomate.util.config import UserOptions, os
from faker.factory import Factory


def _user_settings():
    settings = UserOptions()
    settings.read_settings()
    return settings


def status(provider):
    settings = _user_settings()
    return provider.get_status(settings)


def get_ip(provider):
    settings = _user_settings()
    return provider.get_ip(settings)


def setrootpw(provider, password):
    settings = _user_settings()
    settings.put('rootpw', password)
    return provider.set_rootpw(settings)


def options(provider):
    return provider.options()


def get_network_fee():
    return wallet_util.get_network_fee()


def purchase(provider, vps_option, wallet):
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
