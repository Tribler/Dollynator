import hashlib
import random
import string
import threading
import time
from datetime import datetime

from plebnet.messaging import MessageConsumer
from plebnet.messaging import MessageDeliveryError
from plebnet.messaging import MessageReceiver
from plebnet.messaging import MessageSender


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

    timestamp = str(now())

    random_seed = generate_random_string(5) + parent_id

    random_hash = hashlib.sha256(random_seed.encode('utf-8')).hexdigest()

    return random_hash + timestamp


class Contact:
    """
    Nodes contact.
    """

    """
    id: id of the node.
    host: host of the node.
    port: message receiver listening port
    """

    def __init__(self, id: str, host: str, port: int, first_failure=None):

        self.id = id
        self.host = host
        self.port = port

        self.first_failure = None

    def is_down(self):

        if self.first_failure is None:
            self.first_failure = now()

    def is_up(self):

        if self.first_failure is not None:
            self.first_failure = None

    def is_active(self):

        return self.first_failure is not None


class AddressBook(MessageConsumer):
    """
    Node address book.
    Also shares new contacts with all other nodes in the network.
    """

    """
    self_contact: contact of the owner node of the address book.
    list: initial list of contacts
    receiver_notify_interval: notify interval for incoming messages
    """

    def __init__(self, self_contact: Contact, contacts=None, receiver_notify_interval=1,
                 contact_restore_timeout=3600, inactive_nodes_ping_interval=30):

        if contacts is None:
            contacts = []

        self.receiver = MessageReceiver(self_contact.port, notify_interval=receiver_notify_interval)

        self.contacts = contacts.copy()
        self.receiver.register_consumer(self)
        self.self_contact = self_contact
        self.contact_restore_timeout = contact_restore_timeout
        self.inactive_nodes_ping_interval = inactive_nodes_ping_interval

        threading.Thread(target=self.__start_pinging_inactive_nodes).start()

    def __parse_message(self, raw_message):
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

        try:

            sender = MessageSender(recipient.host, recipient.port)
            sender.send_message(message)

            recipient.is_up()

            return True

        except MessageDeliveryError:

            recipient.is_down()

            return False

    def __delete_contact(self, contact: Contact):
        """
        Removes a contact from the contacts list.
        """
        for known_contact in self.contacts:

            if known_contact.id == contact.id:
                self.contacts.remove(known_contact)

                return

    def __start_pinging_inactive_nodes(self):

        while True:

            for contact in self.contacts:

                if not contact.is_active():

                    if not self.__send_message_to_contact(contact, "ping"):

                        if now() - contact.first_failure > self.contact_restore_timeout:
                            self.__delete_contact(contact)

            time.sleep(self.inactive_nodes_ping_interval)

    def notify(self, message):
        """
        Handles incoming messages.
        message: message to handle
        """

        command, data = self.__parse_message(message)

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


def __demo():
    print("TODO")


if __name__ == '__main__':
    __demo()
