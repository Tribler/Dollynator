import hashlib
import random
import string
import calendar
import time

from plebnet.messaging import MessageConsumer
from plebnet.messaging import MessageSender
from plebnet.messaging import MessageReceiver

from interface import implements

def generate_contact_id(parent_id: str):
    
    def generate_random_string(length):

        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(length))

    timestamp = str(calendar.timegm(time.gmtime()))

    random_seed = generate_random_string(5) + parent_id

    hash = hashlib.sha256(random_seed.encode('utf-8')).hexdigest()

    return hash + timestamp


class Contact:

    def __init__(self, id: str, host: str, port: int):
        
        self.id = id
        self.host = host
        self.port = port


class AddressBook(implements(MessageConsumer)):


    def __init__(self, self_contact: Contact, contacts: list = [], receiver_notify_interval=1):
        
        self.receiver = MessageReceiver(self_contact.port, notifyInterfal=receiver_notify_interval)
        
        self.contacts = contacts.copy()
        self.receiver.register_consumer(self)
        self.self_contact = self_contact


    def parse_message(self, raw_message):

        command = raw_message['command']
        data = raw_message['data']

        return command, data


    def generate_add_contact_message(self, contact: Contact):

        return {
            'command': 'add-contact',
            'data': contact
        }


    def __add_contact(self, contact: Contact):

        if contact.id == self.self_contact.id:

            return

        for known_contact in self.contacts:

            if known_contact.id == contact.id:

                return

        self.contacts.append(contact)

        self.__forward_contact(contact)


    def __forward_contact(self, contact: Contact):
        
        message = self.generate_add_contact_message(contact)

        for known_contact in self.contacts:
            
            if known_contact.id == self.self_contact.id:
                continue 
            
            self.__send_message_to_contact(known_contact, message)
            

    def __send_message_to_contact(self, recipient: Contact, message):
        
        sender = MessageSender(recipient.host, recipient.port)

        sender.send_message(message)

    
    def notify(self, message):

        command, data = self.parse_message(message)

        if command == 'add-contact':

            self.__add_contact(data)


    def create_new_distributed_contact(self, contact: Contact):

        self.contacts.append(contact)

        message = self.generate_add_contact_message(contact)

        for known_contact in self.contacts[:-1]:

            self.__send_message_to_contact(known_contact, message)
            

def __demo():

    port_counter = 8000
    id_counter = 1

    print("Initial node id: " + str(id_counter))
    root_contact = Contact(str(id_counter), '127.0.0.1', port_counter)

    nodes = [AddressBook(root_contact)]

    while True:

        for node in nodes:

            print("Node " + node.self_contact.id + " now has " + str(len(node.contacts)) + " contacts")

        # Incrementing counters
        port_counter += 1
        id_counter += 1

        replicating_node = nodes[random.randint(0, len(nodes) - 1)]
        print("-----------------------------------------------------------------")
        print("Node " + str(replicating_node.self_contact.id) + " is about to replicate:\n\n")

        new_node_contact = Contact(str(id_counter), '127.0.0.1', port_counter)
        new_node_contacts_list = replicating_node.contacts.copy()
        new_node_contacts_list.append(replicating_node.self_contact)
        new_node = AddressBook(new_node_contact, new_node_contacts_list)

        nodes.append(new_node)

        replicating_node.create_new_distributed_contact(new_node.self_contact)

        time.sleep(1)


if __name__ == '__main__':

    __demo()
