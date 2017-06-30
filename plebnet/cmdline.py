import json
import os
import re
import smtplib
import subprocess
import sys
import time
from argparse import ArgumentParser
from subprocess import CalledProcessError

import cloudomate
from cloudomate.cmdline import providers as cloudomate_providers
from cloudomate.util.config import UserOptions
from cloudomate.wallet import Wallet
from plebnet import cloudomatecontroller, twitter
from plebnet.agent import marketapi
from plebnet.agent.dna import DNA
from plebnet.cloudomatecontroller import options
from plebnet.config import PlebNetConfig

TRIBLER_HOME = os.path.expanduser("~/PlebNet/tribler")
PLEBNET_CONFIG = os.path.expanduser("~/.plebnet.cfg")
TIME_IN_HOUR = 60.0 * 60.0
TIME_IN_DAY = TIME_IN_HOUR * 24.0

MAX_DAYS = 5


def execute(cmd=sys.argv[1:]):
    parser = ArgumentParser(description="Plebnet")

    subparsers = parser.add_subparsers(dest="command")
    add_parser_check(subparsers)
    add_parser_setup(subparsers)

    args = parser.parse_args(cmd)
    args.func(args)


def add_parser_check(subparsers):
    parser_list = subparsers.add_parser("check", help="Check plebnet")
    parser_list.set_defaults(func=check)


def add_parser_setup(subparsers):
    parser_list = subparsers.add_parser("setup", help="Setup plebnet")
    parser_list.set_defaults(func=setup)


def setup(args):
    print("Setting up PlebNet")
    cloudomatecontroller.generate_config()
    config = PlebNetConfig()
    config.set('expiration_date', time.time() + 30 * TIME_IN_DAY)
    config.save()

    dna = DNA()
    dna.read_dictionary()
    dna.write_dictionary()
    twitter.tweet_arrival()


def check(args):
    """
    Check whether conditions for buying new server are met and proceed if so
    :param args: 
    :return: 
    """
    print("Checking")
    config = PlebNetConfig()

    dna = DNA()
    dna.read_dictionary()

    if not tribler_running():
        print("Tribler not running")
        success = start_tribler()
        print(success)
        # Now give tribler time to startup
        return success

    #TEMP TO SEE EXITNODE PERFORMANCE
    if not os.path.isfile(os.path.join(TRIBLER_HOME, 'twistd2.pid')):
        env = os.environ.copy()
        env['PYTHONPATH'] = TRIBLER_HOME
        try:
            subprocess.call(['twistd', '--pidfile=twistd2.pid','tunnel_helper', '-x', '-M'], cwd=TRIBLER_HOME, env=env)
            return True
        except CalledProcessError:
            return False
    #TEMP TO SEE EXITNODE PERFORMANCE

    if not config.get('chosen_provider'):
        print ("Choosing new provider")
        update_choice(config, dna)

    if config.time_since_offer() > TIME_IN_HOUR:
        print("Calculating new offer")
        update_offer(config, dna)

    if config.get('chosen_provider'):
        (provider, option, _) = config.get('chosen_provider')
        if marketapi.get_btc_balance() >= calculate_price(provider, option):
            print("Purchase server")
            transaction_hash, provider = purchase_choice(config)
            if transaction_hash:
                config.get('transactions').append(transaction_hash)
                # evolve yourself positively if you are successfull
                own_provider = get_own_provider(dna)
                evolve(own_provider, dna, True)
            else:
                # evolve provider negatively if not succesfull
                evolve(provider, dna, False)

    install_available_servers(config, dna)
    config.save()


def tribler_running():
    """
    Check if tribler is running.
    :return: True if twistd.pid exists in /root/tribler
    """
    return os.path.isfile(os.path.join(TRIBLER_HOME, 'twistd.pid'))


def start_tribler():
    """
    Start tribler
    :return: 
    """
    env = os.environ.copy()
    env['PYTHONPATH'] = TRIBLER_HOME
    try:
        subprocess.call(['twistd', 'plebnet', '-p', '8085', '--exitnode'], cwd=TRIBLER_HOME, env=env)
        return True
    except CalledProcessError:
        return False


def update_offer(config, dna):
    if not config.get('chosen_provider'):
        return
    (provider, option, _) = config.get('chosen_provider')
    btc_price = calculate_price(provider, option) * 1.1
    place_offer(btc_price, config)


def calculate_price(provider, option):
    vpsoption = options(cloudomate_providers[provider])[option]
    gateway = cloudomate_providers[provider].gateway
    btc_price = gateway.estimate_price(
        cloudomate.wallet.get_price(vpsoption.price, vpsoption.currency)) + cloudomate.wallet.get_network_fee()
    return btc_price


def place_offer(chosen_est_price, config):
    """
    Sell all available MC for the chosen estimated price on the Tribler market.
    :param config: config
    :param chosen_est_price: Target amount of BTC to receive
    :return: success of offer placement
    """
    available_mc = marketapi.get_mc_balance()
    if available_mc == 0:
        print("No MC available")
        return False
    config.bump_offer_date()
    config.set('last_offer', {'BTC': chosen_est_price, 'MC': available_mc})
    return marketapi.put_ask(price=chosen_est_price, price_type='BTC', quantity=available_mc, quantity_type='MC',
                             timeout=TIME_IN_HOUR)


def update_choice(config, dna):
    all_providers = dna.vps
    excluded_providers = config.get('excluded_providers')
    available_providers = list(set(all_providers.keys()) - set(excluded_providers))
    providers = {k: all_providers[k] for k in all_providers if k in available_providers}
    print("Providers: %s" % providers)
    if providers >= 1 and sum(providers.values()) > 0:
        providers = DNA.normalize_excluded(providers)
        choice = (provider, option, price) = pick_provider(providers)
        config.set('chosen_provider', choice)
        print("First provider: %s" % provider)


def pick_provider(providers):
    provider = DNA.choose_provider(providers)
    gateway = cloudomate_providers[provider].gateway
    option, price, currency = pick_option(provider)
    btc_price = gateway.estimate_price(
        cloudomate.wallet.get_price(price, currency)) + cloudomate.wallet.get_network_fee()
    return provider, option, btc_price


def pick_option(provider):
    """
    Pick most favorable option at a provider. For now pick cheapest option
    :param provider: 
    :return: (option, price, currency)
    """
    vpsoptions = options(cloudomate_providers[provider])
    cheapestoption = 0
    for item in range(len(vpsoptions)):
        if vpsoptions[item].price < vpsoptions[cheapestoption].price:
            cheapestoption = item

    return cheapestoption, vpsoptions[cheapestoption].price, vpsoptions[cheapestoption].currency


def purchase_choice(config):
    """
    Purchase the cheapest provider in chosen_providers. If buying is successful this provider is moved to bought. In any
    case the provider is removed from choices.
    :param config: config
    :return: success
    """
    (provider, option, _) = config.get('chosen_provider')
    transaction_hash = cloudomatecontroller.purchase(cloudomate_providers[provider], option, wallet=Wallet())
    if transaction_hash:
        config.get('bought').append((provider, transaction_hash))
        config.set('chosen_provider', None)
    if provider not in config.get('excluded_providers'):
        config.get('excluded_providers').append(provider)
    return transaction_hash, provider


def get_own_provider(dna):
    return dna.dictionary['Self']


def evolve(provider, dna, success):
    if success:
        dna.positive_evolve(provider)
    else:
        dna.negative_evolve(provider)


def install_available_servers(config, dna):
    bought = config.get('bought')

    for provider, transaction_hash in bought:
        print("Checking whether %s is activated" % provider)
        try:
            ip = subprocess.check_output(['cloudomate', 'getip', provider])
            print("Installling child on %s " % provider)
            if is_valid_ip(ip):
                user_options = UserOptions()
                user_options.read_settings()
                rootpw = user_options.get('rootpw')
                cloudomatecontroller.setrootpw(cloudomate_providers[provider], rootpw)
                parentname = '{0}-{1}'.format(user_options.get('firstname'), user_options.get('lastname'))
                dna.create_child_dna(provider, parentname, transaction_hash)
                # Save config before entering possibly long lasting process
                config.save()
                success = install_server(ip, rootpw)
                send_child_creation_mail(ip, rootpw, success, config, user_options, transaction_hash)
                # Reload config in case install takes a long time
                config.load()
                config.get('installed').append({provider: success})
                if (provider, transaction_hash) in bought:
                    bought.remove((provider, transaction_hash))
        except CalledProcessError:
            print("%s not ready yet" % provider)


def send_child_creation_mail(ip, rootpw, success, config, user_options, transaction_hash):
    mail_message = 'IP: %s\n' % ip
    mail_message += 'Root password: %s\n' % rootpw
    mail_message += 'Success: %s\n' % success
    mail_message += 'Transaction_hash: %s\n' % transaction_hash
    mail_dna = DNA()
    mail_dna.read_dictionary()
    mail_message += '\nDNA\n%s\n' % json.dumps(mail_dna.dictionary)
    mail_message += '\nConfig\n%s\n' % json.dumps(config.config)
    send_mail(mail_message, user_options.get('firstname') + ' ' + user_options.get('lastname'))


def is_valid_ip(ip):
    return re.match('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip)


def install_server(ip, rootpw):
    file_path = os.path.dirname(os.path.realpath(__file__))
    script_path = os.path.join(file_path, '../scripts/create-child.sh')
    command = '%s %s %s' % (script_path, ip.strip(), rootpw.strip())
    print("Running %s" % command)
    success = subprocess.call(command, shell=True)
    if success:
        print("Installation successful")
    else:
        print("Installation unsuccesful")
    return success


def send_mail(mail_message, name):
    sender = name + '@pleb.net'
    receivers = ['plebnet@heijligers.me']

    mail = """From: %s <%s>
To: Jaap <plebnet@heijligers.me>
Subject: New child spawned

""" % (name, sender)
    mail += mail_message

    try:
        print("Sending mail: %s" + mail)
        smtp = smtplib.SMTP('mail.heijligers.me')
        smtp.sendmail(sender, receivers, mail)
        print "Successfully sent email"
    except smtplib.SMTPException:
        print "Error: unable to send email"


if __name__ == '__main__':
    execute()
