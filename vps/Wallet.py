"""
Created on Apr 26, 2016

@author: niels
"""
from subprocess import PIPE, STDOUT
from Generator import Generator
import subprocess
import re
import os
import time
import sys
import pexpect


class Wallet(object):
    """
    This class will manage the bitcoins going in and out off the agent.
    """

    def __init__(self):
        """ Constructor. """
        output = pexpect.run('electrum listaddresses')
        print(output)
        pattern = re.compile(r'\[\W*"[A-z0-9]+"\W*\]')  # the specific output for electrum if 1 adress exists

        print(pattern.search(output))

        if pattern.search(output):
            # if a wallet exists, initialize that one
            print('using already existing wallet')
        else:
            self._create_wallet()
        subprocess.call(['electrum', 'daemon', 'start'])

    def _answer_prompt(self, child, answer):
        """
        Wait for a prompt, then send the answer. Answering with '' is the same as no answer
        
        child -- a result from pexpect.spawn and is thus of the pexpect.spawn class.
        """

        # wait for prompt, then send answer
        child.waitnoecho()
        child.sendline(answer)
        try:
            child.read()
        except:
            pass  # somethimes no output is generated, and eof would cash read...

    def _create_wallet(self):
        print('did not find an existing wallet, creating a new one')
        # ensure the daemon is stopped, as this causes path errors (mostly usefull for development)
        pexpect.run('electrum daemon stop')
        # build a new wallet if no wallet yet exists
        walletpair = str(subprocess.check_output('python addrgen/addrgen.py', shell=True))
        walletpair = re.split('\W+', walletpair)

        self.address = walletpair[1]
        self.privkey = walletpair[2]
        print('created a wallet with address \'' + self.address + '\' and privatekey \'' + self.privkey + '\'')
        child = pexpect.spawn('electrum', ['restore', self.privkey])
        # respectively: use default password, use default fee (0.002), use default gap limit and give seed
        self._answer_prompt(child, '')

        # check if wallet was created succesfulyl
        command = """electrum listaddresses"""
        output = pexpect.run(command)

        walletFinder = re.compile(r'\[\W*"([A-z0-9]+)"\W*\]')

        result = walletFinder.search(output)

        # This horrible feedback loop is here due to a quirk of electrum.
        # Needs refactoring, but do not refactor without extensive testing (i.e. multiple vps all from clean install)
        # Because electrum behaviour right after startup tends to differ from server to server (i suspect something to do wtih specs)
        try:
            print result.group(1)
            return result.group(1)
        except:
            return self._create_wallet()

    # def __del__(self):
    #     '''
    #     clear up the electrum service
    #     '''
    #     subprocess.call(['electrum', 'daemon', 'stop'])

    def balance(self):
        """
        Return the balance of the Btc wallet (i.e. confirmed balance+unconfirmed balance).
        """
        balancesheet = str(subprocess.check_output(['electrum', 'getbalance']))
        return self.calculateBalance(balancesheet)

    def calculateBalance(self, balancesheet):
        """
        Given the output of electrum getbalance
        calculates the actual balance.
        """
        confirmedBalance = re.search('"confirmed": "([0-9.\-]+)"', balancesheet)
        unconfirmedBalance = re.search('"unconfirmed": "([0-9.\-]+)"', balancesheet)

        sum = 0.0
        if confirmedBalance:
            sum += float(confirmedBalance.group(1))
        if unconfirmedBalance:
            sum += float(unconfirmedBalance.group(1))
        return sum

    def canPay(self, amount, fee):
        return float(amount) + float(fee) <= self.balance()

    def payToAutomatically(self, address, amount):
        """
        Make a payment using an automatically calculated fee.

        address -- The address to transfer to.
        amount -- The amount to transfer.
        """
        if self.canPay(amount, '0.0'):
            payment = str(subprocess.check_output(['electrum', 'payto', address, amount]))

            # filter out the hex code from the payment and broadcast this
            hex = re.search('hex": "([A-z0-9]+)"', payment).group(1)
            subprocess.call(['electrum', 'broadcast', hex])

            return True
        return False

    def send_everything_to(self, address):
        """
        Transfers all available funds in the wallet to the specified address
        address -- The address as string to transfer to
        """
        payment = str(subprocess.check_output(['electrum', 'payto', str(address), '!']))

        # filter out the hex code from the payment and broadcast this
        hex = re.search('hex": "([A-z0-9]+)"', payment).group(1)
        subprocess.call(['electrum', 'broadcast', hex])

    def payTo(self, address, fee, amount):
        """
        If funds allow, transfer amount in Btc to Address. With a fee for
        processor.

        address -- The address to pay to.
        fee -- The fee to pay.
        amount -- The amount to transfer.
        """
        if self.canPay(amount, fee):
            print(str(subprocess.call(['electrum', 'payto', '-f', fee, address, amount])))
