import threading
import time

from plebnet.messaging import Contact
from plebnet.messaging import MessageConsumer
from plebnet.messaging import MessageDeliveryError
from plebnet.messaging import MessageReceiver
from plebnet.messaging import MessageSender
from plebnet.messaging import now


def generate_contact_id(parent_id: str = ""):
    """
    Generates a random, virtually unique id for a new node.
    :param parent_id: id of the parent node, defaults to empty
    :return: the generated id
    """

    def generate_random_string(length):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(length))

    timestamp = str(now())

    random_seed = generate_random_string(5) + parent_id

    random_hash = hashlib.sha256(random_seed.encode('utf-8')).hexdigest()

    return random_hash + timestamp


class AddressBook(MessageConsumer):
    """
    Node address book, responsible for sharing new contacts and deleting inactive ones.
    """

    def __init__(
            self,
            self_contact: Contact,
            contacts=None,
            receiver_notify_interval=1,
            contact_restore_timeout=3600,
            inactive_nodes_ping_interval=1799
    ):
        """
        Initializes a new address book.
        :param self_contact: contact of the owner of the address book
        :param contacts: contacts in the address book
        :param receiver_notify_interval: interval at which the message receiver notifies of new messages
        :param contact_restore_timeout: timeout of pinging of inactive nodes before deletion
        :param inactive_nodes_ping_interval: interval for pinging inactive nodes
        """

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
        Parses a raw message for internal processing.
        :param raw_message: raw message to parse
        """

        command = raw_message['command']
        data = raw_message['data']

        return command, data

    def __generate_add_contact_message(self, contact: Contact):
        """
        Generates an "add-contact" message.
        :param contact: add-contact message payload
        """

        return {
            'command': 'add-contact',
            'data': contact
        }

    def __add_contact(self, contact: Contact):
        """
        Handles incoming "add-contacts" commands.
        :param contact: contact to add
        """

        self.create_new_distributed_contact(contact)

    def __forward_contact(self, contact: Contact):
        """
        Forwards a contact to all other known contacts.
        :param contact: contact to forward
        """

        message = self.__generate_add_contact_message(contact)

        for known_contact in self.contacts:

            # Prevent notifying a contact of themselves
            if known_contact.id == contact.id:
                continue

            # Prevent node notifying itself
            if known_contact.id == self.self_contact.id:
                continue

            # print("Node " + self.self_contact.id + " forwards " + contact.id + "'s contact to " + known_contact.id)

            self.send_message_to_contact(known_contact, message)

    def send_message_to_contact(self, recipient: Contact, message):
        """
        Sends a message to a contact, and marks the link to the recipient as either up or down.
        :param recipient: recipient node's contact
        :param message: message to send
        :return: True iff the delivery of the message was successful
        """

        try:

            sender = MessageSender(recipient.host, recipient.port)
            sender.send_message(message)

            self.__set_link_state(True, recipient)

            return True

        except MessageDeliveryError:
            
            self.__set_link_state(False, recipient)

            return False
    
    def __set_link_state(self, link_up: bool, contact: Contact):
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
        
                    # print("Node " + self.self_contact.id + " sees " + contact.id + " as down")
                    known_contact.link_down()


    def __delete_contact(self, contact: Contact):
        """
        Deletes a contact from the contact list.
        :param contact: contact to delete
        :return:
        """

        # print("Node " + self.self_contact.id + " deletes " + contact.id + "'s contact")

        for known_contact in self.contacts:

            if known_contact.id == contact.id:

                self.contacts.remove(known_contact)

                return

    def __generate_ping_message(self):

        return {
            'command': 'ping',
            'data': None
        }

    def __start_pinging_inactive_nodes(self):
        """
        Starts periodically pinging inactive nodes.
        """
        
        while True:

            time.sleep(self.inactive_nodes_ping_interval)

            for contact in self.contacts:

                if not contact.is_active():
    
                    ping_message = self.__generate_ping_message()

                    if not self.send_message_to_contact(contact, ping_message):

                        current_timestamp = now()
    
                        if current_timestamp - contact.first_failure > self.contact_restore_timeout:
        

                            self.__delete_contact(contact)


    def notify(self, message):
        """
        Handles incoming messages.
        :param message: message to handle
        """

        command, data = self.__parse_message(message)

        if command == 'add-contact':
            self.__add_contact(data)

    def create_new_distributed_contact(self, contact: Contact):
        """
        Adds new contact and notifies the network.
        :param contact: new contact
        """

        if self.__append_contact(contact):

            # print("Node " + self.self_contact.id + " adds " + contact.id + "'s contact")

            self.__forward_contact(contact)

    def __append_contact(self, contact: Contact):
        """
        Appends a contact to the contacts list.
        :param contact: contact to append to the contacts list
        """

        if contact.id == self.self_contact.id:

            return False

        for known_contact in self.contacts:
            
            if known_contact.id == contact.id:
                
                return False

        self.contacts.append(contact)

        return True

def __demo():
    
    id_counter = 1
    port_counter = 8001

    ping_interval = 1
    restore_timeout = 0

    root_contact = Contact(str(id_counter), "127.0.0.1", port_counter)

    nodes = [AddressBook(root_contact, contact_restore_timeout=restore_timeout, inactive_nodes_ping_interval=ping_interval, receiver_notify_interval=0.01)]

    while True:

        port_counter += 1
        id_counter += 1

        replicating_node = random.choice(nodes)

        print("Node " + replicating_node.self_contact.id + " replicates: \n")

        new_node_contact_list = replicating_node.contacts.copy()
        new_node_contact_list.append(replicating_node.self_contact)

        new_node_contact = Contact(str(id_counter), '127.0.0.1', port_counter)

        nodes.append(AddressBook(new_node_contact, new_node_contact_list, contact_restore_timeout=restore_timeout, inactive_nodes_ping_interval=ping_interval, receiver_notify_interval=0.01))

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

    
if __name__ == '__main__':

    __demo()
