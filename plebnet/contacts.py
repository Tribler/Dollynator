import hashlib
import random
import string
import calendar
import time
from copy import deepcopy

from plebnet.messaging import MessageSender
from plebnet.messaging import MessageReceiver


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

    def __init__(self, id: str, host: str, port: int):
        self.id = id
        self.host = host
        self.port = port


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

    def __init__(self, self_contact: Contact, contacts: list = [], receiver_notify_interval=1):

        self.receiver = MessageReceiver(self_contact.port, notify_interval=receiver_notify_interval)

        self.contacts = deepcopy(contacts)
        self.receiver.register_consumer(self)
        self.self_contact = self_contact

    def parse_message(self, raw_message):
        """
        Parses a raw message into command and data.
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

    def notify(self, message):
        """
        Handles incoming messages.
        message: message to handle
        """
        command, data = self.parse_message(message)

        if command == 'add-contact':
            self.__add_contact(data)




    def create_new_distributed_contact(self, contact: Contact):
        """
        Adds new contact and notifies the network.
        contact: new contact
        """

        self.contacts.append(contact)

        message = self.__generate_add_contact_message(contact)

        for known_contact in self.contacts[:-1]:
            self.__send_message_to_contact(known_contact, message)

    def __send_message_to_contact(self, recipient: Contact, message):
        """
        Sends a message to a contact.
        recipient: recipient node's contact
        message: message to send
        """

        sender = MessageSender(recipient.host, recipient.port)

        sender.send_message(message)



def __demo():
    port_counter = 8000
    id_counter = 1

    print("Initial node id: " + str(id_counter))
    root_contact = Contact(str(id_counter), '127.0.0.1', port_counter)

    nodes = [AddressBook(root_contact, receiver_notify_interval=0.1)]

    max_nodes = 10
    i = 0

    while i < max_nodes:

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
        new_node = AddressBook(new_node_contact, new_node_contacts_list, receiver_notify_interval=0.1)

        nodes.append(new_node)

        replicating_node.create_new_distributed_contact(new_node.self_contact)

        time.sleep(1)

        i += 1

    while True:

        print("-----------------------------------------------------------------")
        for node in nodes:
            print("Node " + node.self_contact.id + " now has " + str(len(node.contacts)) + " contacts")

        time.sleep(5)


if __name__ == '__main__':
    __demo()
