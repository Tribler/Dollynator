import hashlib
import random
import string
import calendar
import time
import argparse
import getpass
import os
import socket

from datetime import datetime
from crontab import CronTab

from plebnet.messaging import MessageSender
from plebnet.messaging import MessageConsumer
from plebnet.messaging import MessageReceiver

def now():
    """
    Returns the current timestamp.
    """
    return int(datetime.timestamp(datetime.now()))


def generate_contact_id(parent_id: str = ""):
    """
    Generates a contact id for a node children.
    parent_id: id of the parent. Use "" if node has no parent.
    """
    def generate_random_string(length):

        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(length))

    timestamp = str(calendar.timegm(time.gmtime()))

    random_seed = generate_random_string(5) + parent_id

    hash = hashlib.sha256(random_seed.encode('utf-8')).hexdigest()

    return hash + timestamp


class Contact:
    """
    Nodes contact.
    """

    """
    id: id of the node.
    host: host of the node.
    port: message receiver listening port
    """
    def __init__(self, id: str, host: str, port: int, first_failure = None):
        
        self.id = id
        self.host = host
        self.port = port

        self.first_failure = None

    def __get_ping_command(self, ab_port):

        command = "PYTHONPATH=" + os.getcwd()
        command += " python3 -m plebnet.contacts -p"
        command += " --host " + self.host
        command += " --port " + str(self.port)
        command += " --ab-port " + str(ab_port)

        return command


    def __job_comment(self):

        return "ping " + self.id + " " + self.host + " " + str(self.port)


    def did_not_reply(self, ab_port, minutes_interval = 30):

        if self.first_failure is None:

            self.first_failure = now()

        cron = CronTab(user=True)
        job = cron.new(command = self.__get_ping_command(ab_port), comment=self.__job_comment())
        job.minute.every(minutes_interval)

        cron.write()
       

    def replied(self):

        if self.first_failure is not None:

            self.first_failure = None
            self.remove_ping_job()    


    def remove_ping_job(self):

        cron = CronTab()
        for job in cron:
            if job.comment == self.__job_comment():
                cron.remove(job)
                cron.write()
        

    def is_active(self):

        return self.first_failure is not None


class AddressBook:
    """
    Node address book.
    Also shares new contacts with all other nodes in the network.
    """

    """
    self_contact: contact of the owner node of the address book.
    list: initial list of contacts
    receiver_notify_interval: notify interval for incoming messages
    """
    def __init__(self, self_contact: Contact, contacts: list = [], receiver_notify_interval=1, contact_restore_timeout=3600, inactive_nodes_ping_interval=30):
        
        self.receiver = MessageReceiver(self_contact.port, notify_interval=receiver_notify_interval)
        
        self.contacts = contacts.copy()
        self.receiver.register_consumer(self)
        self.self_contact = self_contact
        self.contact_restore_timeout = contact_restore_timeout
        self.inactive_nodes_ping_interval = inactive_nodes_ping_interval


    def parse_message(self, raw_message):
        """
        Parses a raw message into comamnd and data.
        raw_message: raw_message to parse
        """
        command = raw_message['command']
        data = raw_message['data']

        return command, data


    def __generate_add_contact_message(self, contact: Contact):
        """
        Generates an "add-contact" message.
        contact: add-contact message payload
        """
        
        return {
            'command': 'add-contact',
            'data': contact
        }


    def __generate_ping_unsuccessful_message(self, contact: Contact):
        """
        Generates an "ping-unsuccessful" message.
        contact: ping-unsuccessful message payload
        """
        
        return {
            'command': 'ping-unsuccessful',
            'data': contact
        }


    def __generate_ping_successful_message(self, contact: Contact):
        """
        Generates an "ping-successful" message.
        contact: ping-successful message payload
        """
        
        return {
            'command': 'ping-successful',
            'data': contact
        }


    def __add_contact(self, contact: Contact):
        """
        Handles incoming "add-contacts" commands.
        contact: contact to add
        """

        if contact.id == self.self_contact.id:

            # Contact is self
            return

        for known_contact in self.contacts:

            if known_contact.id == contact.id:

                # Contact is already known
                return

        # Contact is added and forwarded

        self.contacts.append(contact)

        self.__forward_contact(contact)


    def __forward_contact(self, contact: Contact):
        """
        Forwards new contact to all other known contacts.
        contact: new contact
        """
        
        message = self.__generate_add_contact_message(contact)

        for known_contact in self.contacts:
            
            # Prevent notifying a contact of themselves
            if known_contact.id == contact.id:
                continue 
            
            self.__send_message_to_contact(known_contact, message)
            

    def __send_message_to_contact(self, recipient: Contact, message):
        """
        Sends a message to a contact.
        recipient: recipient node's contact
        message: message to send
        """

        sender = MessageSender(recipient.host, recipient.port)

        try:

            sender.send_message(message)

        except:
            
            recipient.did_not_reply(self.self_contact.port, minutes_interval=self.inactive_nodes_ping_interval)
    

    def __delete_contact(self, contact: Contact):
        """
        Deletes a contact.
        """
        for known_contact in self.contacts:
            
            if known_contact.id == contact.id:

                self.contacts.remove(known_contact)

                known_contact.remove_ping_job()

                return


    def __ping_successful(self, contact: Contact):

        contact.replied()


    def __ping_unsuccessful(self, contact: Contact):

        for known_contact in self.contacts:

            if contact.id == known_contact.id:
                
                if now() - known_contact.first_failure > self.contact_restore_timeout:
                    
                    self.__delete_contact(known_contact)
    

    def notify(self, message):
        """
        Handles incoming messages.
        message: message to handle
        """
        command, data = self.parse_message(message)

        if command == 'add-contact':

            self.__add_contact(data)

        elif command == 'ping-unsuccessful':
            
            self.__ping_unsuccessful(data)

        elif command == 'ping-successful':

            self.__ping_successful(data)


    def create_new_distributed_contact(self, contact: Contact):
        """
        Adds new contact and notifies the network.
        contact: new contact
        """

        self.contacts.append(contact)

        message = self.__generate_add_contact_message(contact)

        for known_contact in self.contacts[:-1]:

            self.__send_message_to_contact(known_contact, message)
    

def __demo():

    port_counter = 8001
    id_counter = 1

    nodes = []

    root_contact = Contact(str(id_counter), '127.0.0.1', port_counter)

    nodes.append(AddressBook(root_contact, receiver_notify_interval=0.01, contact_restore_timeout=1, inactive_nodes_ping_interval=1))

    while True:

        print("")

        id_counter += 1
        port_counter += 1

        replicating_node = random.choice(nodes)

        print("Node " + replicating_node.self_contact.id + " is replicating")

        new_node_contact = Contact(str(id_counter), '127.0.0.1', port_counter)

        new_node_contact_list = replicating_node.contacts.copy()
        new_node_contact_list.append(replicating_node.self_contact)

        nodes.append(AddressBook(new_node_contact, new_node_contact_list, receiver_notify_interval=0.01, contact_restore_timeout=1, inactive_nodes_ping_interval=1))

        replicating_node.create_new_distributed_contact(new_node_contact)

        print("")
        
        time.sleep(28)

        for node in nodes:

            contacts = ""

            for contact in node.contacts:

                contacts += contact.id + ", "


            print("Node " + node.self_contact.id + " has contacts: " + contacts)

        for i in range(int(len(nodes) / 2)):

            node_to_kill = random.choice(nodes)
            print("Killing node " + node_to_kill.self_contact.id)

            node_to_kill.receiver.kill()
            nodes.remove(node_to_kill)

        time.sleep(1)


def __ping_host(host: str, port: int, ab_port: int, contact_id: str):

    ping_sender = MessageSender(host, port)
    ab_sender = MessageSender('127.0.0.1', ab_port)

    pinged_contact = Contact(contact_id, host, port)

    try:
        ping_sender.send_message("Helo")

    except:

        print("Host down")
        ab_sender.send_message(ab_sender.__generate_ping_unsuccessful_message(pinged_contact))
        return

    ab_sender.send_message(ab_sender.__generate_ping_successful_message(pinged_contact))

    

if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument("-d", "--demo", action='store_true', help="Run demo")

    parser.add_argument("-p", "--ping-node", action='store_true')
    parser.add_argument("--host")
    parser.add_argument("--port", type=int)
    parser.add_argument("--ab-port", type=int)
    parser.add_argument("--test", action='store_true')
    parser.add_argument("--test-receiver", action='store_true')
    parser.add_argument("--contact-id")
    
    args = parser.parse_args()

    if args.demo:

        __demo()


    elif args.ping_node:

        if args.host is None:

            print("No host was specified")
            exit(1)

        if args.port is None:

            print("No port was specified")
            exit(1)
            
        if args.ab_port is None:

            print("No self port was specified")
            exit(1)

        if args.contact_id is None:

            print("No contact id specified")
            exit(1)

        __ping_host(args.host, args.port, args.ab_port, args.contact_id)
