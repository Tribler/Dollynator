import json
import os
import re
import smtplib
import subprocess
import sys
import time
from argparse import ArgumentParser
from subprocess import CalledProcessError

import copy
import electrum
from cloudomate.wallet import Wallet
from electrum import Wallet as ElectrumWallet
from electrum import WalletStorage
from electrum import keystore
from electrum.mnemonic import Mnemonic

from plebnet import cloudomatecontroller, twitter
from plebnet.agent import marketapi
from plebnet.agent.dna import DNA
from plebnet.config import PlebNetConfig

WALLET_FILE = os.path.expanduser("~/.electrum/wallets/default_wallet")
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
    create_wallet()


def create_wallet():
    """
    Create an electrum wallet if it does not exist
    :return: 
    """
    if not os.path.isfile(WALLET_FILE):
        print("Creating wallet")
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
        print("Your wallet generation seed is:\n\"%s\"" % seed)
        print("Please keep it in a safe place; if you lose it, you will not be able to restore your wallet.")
        wallet.storage.write()
        print("Wallet saved in '%s'" % wallet.storage.path)
    else:
        print("Wallet already present")


def check(args):
    """
    Start plebnet check, first load all data structures and make sure no other check is running.
    :param args: 
    :return: 
    """
    try:
        if os.path.isfile(os.path.join(TRIBLER_HOME, 'plebnet.pid')):
            print("Plebnet Check is already running")
            return
        with open(os.path.join(TRIBLER_HOME, 'plebnet.pid'), 'r') as f:
            f.write(str(time.time()))

        print("Checking")
        config = PlebNetConfig()
        config_backup = copy.deepcopy(config)
        dna = DNA()
        dna.read_dictionary()
        start_check(config, dna)
        print("Done checking")
    except BaseException as e:
        print("Error caught in check function")
        print(e)
        print("Old configuration:")
        print(config_backup)
        print("New configuration:")
        print(config)
        print("Resuming check")
    finally:
        print("Start check cleanup")
        if os.path.isfile(os.path.join(TRIBLER_HOME, 'plebnet.pid')):
            os.remove(os.path.join(TRIBLER_HOME, 'plebnet.pid'))
        config.save()
        print("Done with check cleanup")


def start_check(config, dna):
    """
    Execute commands based on state of config
    :param config: 
    :param dna: 
    :return: 
    """
    start_tribler()

    if config.get('bought'):
        print("Installing servers")
        install_available_servers(config, dna)
    else:
        print("No servers to install")

    if not config.get('chosen_provider'):
        print ("Choosing new provider")
        update_choice(config, dna)
    else:
        print("Server already chosen: {0}".format(config.get('chosen_provider')))

    if config.time_since_offer() > TIME_IN_HOUR:
        print("Calculating new offer")
        update_offer(config, dna)
    else:
        print("Last offer has not yet expired")

    if config.get('chosen_provider'):
        print("Attempting Purchase of chosen provider")
        attempt_purchase(config, dna)
    else:
        print("No chosen provider set or done choosing")


def attempt_purchase(config, dna):
    """
    Attempt to purchase the chosen provider
    :param config: 
    :param dna: 
    :return: 
    """
    (provider, option, _) = config.get('chosen_provider')
    if marketapi.get_btc_balance() >= cloudomatecontroller.estimate_price(provider, option):
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
    else:
        print("Insufficient balance to purchase server")


def tribler_running():
    """
    Check if tribler is running.
    :return: True if twistd.pid exists in /root/tribler
    """
    return os.path.isfile(os.path.join(TRIBLER_HOME, 'twistd.pid'))


def start_tribler():
    if not tribler_running():
        print("Tribler not running")
        success = run_tribler()
        print(success)
        # Now give tribler time to startup
        return success

    # TEMP TO SEE EXITNODE PERFORMANCE, tunnel_helper should be merged with market or other way around
    if not os.path.isfile(os.path.join(TRIBLER_HOME, 'twistd2.pid')):
        env = os.environ.copy()
        env['PYTHONPATH'] = TRIBLER_HOME
        try:
            subprocess.call(['twistd', '--pidfile=twistd2.pid', 'tunnel_helper', '-x', '-M'], cwd=TRIBLER_HOME, env=env)
            return True
        except CalledProcessError:
            return False
    # TEMP TO SEE EXITNODE PERFORMANCE

def run_tribler():
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
    btc_price = 1.15 * cloudomatecontroller.estimate_price(provider, option)
    place_offer(btc_price, config)


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
    price_per_unit = chosen_est_price / float(available_mc)
    return marketapi.put_ask(price=price_per_unit, price_type='BTC', quantity=available_mc, quantity_type='MC',
                             timeout=TIME_IN_HOUR)


def update_choice(config, dna):
    """
    Choose a new provider and option to try an purchase
    :param config: 
    :param dna: 
    :return: 
    """
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
    else:
        print("No providers left")
        print("Continuing as exit node only")
        sys.exit()


def pick_provider(providers):
    """
    Pick provider and calculate option which is most favorable
    :param providers: 
    :return: 
    """
    provider = DNA.choose_provider(providers)
    option, price, currency = pick_option(provider)
    btc_price = cloudomatecontroller.estimate_price(provider, option)
    return provider, option, btc_price


def pick_option(provider):
    """
    Pick most favorable option at a provider. For now pick cheapest option
    :param provider: 
    :return: (option, price, currency)
    """
    vpsoptions = cloudomatecontroller.options(provider)
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
    transaction_hash = cloudomatecontroller.purchase(provider, option, wallet=Wallet())

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
            ip = cloudomatecontroller.get_ip(cloudomate_providers[provider])
        except BaseException as e:
            print(e)
            print("%s not ready yet" % provider)
            return

        print("Installling child on %s " % provider)
        if is_valid_ip(ip):
            # reset browser, since login requires browser not currently logged in (get_ip is logged in)
            cloudomatecontroller.reset_browser(provider)
            user_options = cloudomatecontroller._user_settings()
            rootpw = user_options.get('rootpw')
            cloudomatecontroller.setrootpw(provider, rootpw)
            parentname = '{0}-{1}'.format(user_options.get('firstname'), user_options.get('lastname'))
            dna.create_child_dna(provider, parentname, transaction_hash)
            # Save config before entering possibly long lasting process
            config.save()
            success = install_server(ip, rootpw)
            send_child_creation_mail(ip, rootpw, success, config, user_options, transaction_hash)
            # Reload config in case install takes a long time
            config.load()
            config.get('installed').append({provider: success})
            if [provider, transaction_hash] in bought:
                bought.remove([provider, transaction_hash])


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
    script_path = os.path.join(file_path, '/root/PlebNet/scripts/create-child.sh')
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
