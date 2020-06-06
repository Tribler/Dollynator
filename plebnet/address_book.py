import random
import threading
import time
from copy import deepcopy

import rsa

from plebnet.messaging import Contact
from plebnet.messaging import Message
from plebnet.messaging import MessageConsumer
from plebnet.messaging import MessageDeliveryError
from plebnet.messaging import MessageReceiver
from plebnet.messaging import MessageSender
from plebnet.messaging import now
from plebnet.messaging import generate_contact_key_pair


class AddressBook(MessageConsumer):
    """
    Node address book, responsible for sharing new contacts and deleting inactive ones.
    """
    _messaging_channel = 'network'

    def __init__(
            self,
            self_contact: Contact,
            private_key: rsa.PrivateKey,
            contacts=None,
            receiver_notify_interval=1.0,
            contact_restore_timeout=3600,
            inactive_nodes_ping_interval=1799
    ):
        """
        Initializes a new address book.
        :param self_contact: contact of the owner of the address book
        :param private_key: private key of the message receiver
        :param contacts: list of known contacts
        :param receiver_notify_interval: interval at which the message receiver notifies of new messages
        :param contact_restore_timeout: timeout of pinging of inactive nodes before deletion
        :param inactive_nodes_ping_interval: interval for pinging inactive nodes
        """

        if contacts is None:
            contacts = []

        self.contacts = deepcopy(contacts)
        self._private_key = private_key

        self.receiver = MessageReceiver(
            port=self_contact.port,
            private_key=self._private_key,
            contacts=self.contacts,
            notify_interval=receiver_notify_interval
        )

        self.receiver.register_consumer(channel=self._messaging_channel, message_consumer=self)

        self.self_contact = self_contact
        self._contact_restore_timeout = contact_restore_timeout
        self._inactive_nodes_ping_interval = inactive_nodes_ping_interval

        threading.Thread(target=self._start_pinging_inactive_nodes).start()

    def kill(self):

        try:
            self.receiver.kill()
        except:
            pass            

    def _generate_add_contact_message(self, contact: Contact) -> Message:
        """
        Generates an "add-contact" message.
        :param contact: contact to add
        """

        return Message(
            channel=self._messaging_channel,
            command='add-contact',
            data=contact
        )

    def _add_contact(self, contact: Contact) -> None:
        """
        Handles incoming "add-contacts" commands.
        :param contact: contact to add
        """

        self.create_new_distributed_contact(contact)

    def _forward_contact(self, contact: Contact) -> None:
        """
        Forwards a contact to all other known contacts.
        :param contact: contact to forward
        """

        message = self._generate_add_contact_message(contact)

        for known_contact in self.contacts:

            # Prevent notifying a contact of themselves
            if known_contact.id == contact.id:
                continue

            # Prevent node notifying itself
            if known_contact.id == self.self_contact.id:
                continue

            self.send_message_to_contact(known_contact, message)

    def send_message_to_contact(self, recipient: Contact, message: Message) -> bool:
        """
        Sends a message to a contact, and marks the link to the recipient as either up or down.
        :param recipient: recipient node's contact or recipient node's contact id
        :param message: message to send
        :return: True iff the delivery of the message was successful
        """

        try:

            sender = MessageSender(recipient)
            sender.send_message(message, self.self_contact.id, self._private_key)

            self._set_link_state(True, recipient)

            return True

        except MessageDeliveryError:

            self._set_link_state(False, recipient)

            return False

    def _set_link_state(self, link_up: bool, contact: Contact) -> None:
        """
        Sets the link with a node's state.
        :param link_up: state to set
        :param contact: contact to set the link's state of
        """

        for known_contact in self.contacts:

            if known_contact.id == contact.id:

                if link_up:

                    known_contact.link_up()

                else:

                    known_contact.link_down()

    def _delete_contact(self, contact: Contact) -> None:
        """
        Deletes a contact from the contact list.
        :param contact: contact to delete
        :return:
        """

        for known_contact in self.contacts:

            if known_contact.id == contact.id:
                self.contacts.remove(known_contact)

                return

    def _generate_ping_message(self) -> Message:
        """
        Generates a ping message
        :return: the generated ping message
        """

        return Message(
            channel=self._messaging_channel,
            command="ping"
        )

    def _start_pinging_inactive_nodes(self) -> None:
        """
        Starts periodically pinging inactive nodes.
        """

        while not self.receiver.kill_flag:

            time.sleep(self._inactive_nodes_ping_interval)

            if self.receiver.kill_flag:
                return

            for contact in self.contacts:

                if not contact.is_active():

                    ping_message = self._generate_ping_message()

                    if not self.send_message_to_contact(contact, ping_message):

                        current_timestamp = now()

                        if current_timestamp - contact.first_failure > self._contact_restore_timeout:

                            self._delete_contact(contact)

    def notify(self, message: Message, sender_id) -> None:
        """
        Handles incoming messages.
        :param sender_id: id of the message sender
        :param message: message to handle
        """

        if message.command == 'add-contact':
            self._add_contact(message.data)

    def create_new_distributed_contact(self, contact: Contact) -> None:
        """
        Adds new contact and notifies the network.
        :param contact: new contact
        """

        if self._append_contact(contact):
            self._forward_contact(contact)

    def _append_contact(self, contact: Contact) -> bool:
        """
        Appends a contact to the contacts list.
        :param contact: contact to append to the contacts list
        :return: true iff the contact list has changed as a result of the operation
        """

        if contact.id == self.self_contact.id:
            return False

        for known_contact in self.contacts:

            if known_contact.id == contact.id:
                return False

        self.contacts.append(contact)

        return True


def _demo():  # pragma: no cover
    id_counter = 1
    port_counter = 8001

    ping_interval = 1
    restore_timeout = 0
    receiver_notify_interval = 0.5

    root_pub, root_priv = generate_contact_key_pair()
    root_contact = Contact(
        id=str(id_counter),
        host="127.0.0.1",
        port=port_counter,
        public_key=root_pub
    )

    root = AddressBook(
        self_contact=root_contact,
        private_key=root_priv,
        contact_restore_timeout=restore_timeout,
        inactive_nodes_ping_interval=ping_interval,
        receiver_notify_interval=receiver_notify_interval
    )

    nodes = [root]

    while True:

        port_counter += 1
        id_counter += 1

        replicating_node = random.choice(nodes)

        print("Node " + replicating_node.self_contact.id + " replicates: \n")

        new_node_contact_list = replicating_node.contacts.copy()
        new_node_contact_list.append(replicating_node.self_contact)

        pub, priv = generate_contact_key_pair()

        new_node_contact = Contact(
            id=str(id_counter),
            host='127.0.0.1',
            port=port_counter,
            public_key=pub
        )

        new_node = AddressBook(
            self_contact=new_node_contact,
            private_key=priv,
            contacts=new_node_contact_list,
            contact_restore_timeout=restore_timeout,
            inactive_nodes_ping_interval=ping_interval,
            receiver_notify_interval=receiver_notify_interval
        )

        nodes.append(new_node)

        replicating_node.create_new_distributed_contact(new_node_contact)

        time.sleep(1)

        for node in nodes:

            contacts = ""

            for contact in node.contacts:
                contacts += contact.id + ", "

            print("Node " + node.self_contact.id + " has " + str(len(node.contacts)) + " contacts: " + contacts)

        time.sleep(1)

        for i in range(int(len(nodes) / 3)):
            node_to_remove = random.choice(nodes)
            print("Killing node " + node_to_remove.self_contact.id)
            node_to_remove.receiver.kill()
            nodes.remove(node_to_remove)

        time.sleep(3)

        print("")


if __name__ == '__main__':  # pragma: no cover
    _demo()
