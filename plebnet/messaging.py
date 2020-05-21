import pickle
import socket
import collections
import threading
import time
import rsa
import random
import string
import hashlib

from datetime import datetime

def now():
    """
    Gets the current timestamp in seconds.
    :return: current timestamp as integer
    """
    return int(datetime.timestamp(datetime.now()))


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



class Contact:
    """
    Nodes contact.
    """

    def __init__(self, id: str, host: str, port: int, public_key: rsa.PublicKey, first_failure=None):
        """
        Instantiates a contact
        :param id: id of the node
        :param host: host of the node
        :param port: port of the node
        :param first_failure: first time of failure of communication with the node
        """

        self.id = id
        self.host = host
        self.port = port
        self.public_key = public_key
        self.first_failure = first_failure

    def link_down(self):
        """
        Sets the node link as down, by storing the current time as first_failure, if not set already.
        """

        if self.first_failure is None:
            self.first_failure = now()

    def link_up(self):
        """
        Sets the node link as up, by clearing the first_failure field
        """

        if self.first_failure is not None:
            self.first_failure = None

    def is_active(self):
        """
        Checks whether the contact is active.
        :return: true iff the contact is active
        """

        return self.first_failure is None

class MessageDeliveryError(Exception):

    def __init__(self, *args):

        if args:

            self.message = args[0]

        else:

            self.mesage = "Message delivery failed"


class MessageConsumer:

    def notify(self, message, sender_id):

        pass


class MessageSender:
    """
    Class for sending messages to MessageReceivers.
    """    
    def __init__(self, receiver: Contact):
        """
        host: Receipient host name.
        port: Receipient port
        """
        self.receiver = receiver
        

    def send_message(self, data, sender_contact_id, private_key, ack_timeout=5.0):
        """
        Sends a message.
        data: message payload
        """

        try:
            # Pickling and encrypting message
            message_body = rsa.encrypt(pickle.dumps(data), self.receiver.public_key)
            signature = rsa.sign(message_body, private_key, "SHA-1")
            
            # Connecting to receiver
            s = socket.socket()
            s.connect((self.receiver.host, self.receiver.port))

            # Sending sender id
            s.send(sender_contact_id.encode('utf-8'))        
            s.settimeout(ack_timeout)
            s.recv(1)

            # Sending size of message
            s.send(str(len(message_body)).encode('utf-8'))
            s.settimeout(ack_timeout)
            s.recv(1)
            
            # Send signature
            s.send(signature)
            s.settimeout(ack_timeout)
            s.recv(1)

            # Sending message
            s.send(message_body)

            s.close()

            

        except:

            raise MessageDeliveryError()



class MessageReceiver:
    """
    Message receiving service. Opens a socket on the specified port, and notifies
    registered consumers when new messages are received.
    """

    """
    port: port to open listening socket on.
    connections_queue_size: size of the connections queue.
    notify_interval: (seconds) interval at which message consumers are notified.
    """

    def __init__(
        self,
        port: int,
        private_key: rsa.PrivateKey,
        contacts: list,
        connections_queue_size: int = 20,
        notify_interval: int = 1
    ):

        self.port = port
        self.private_key = private_key
        self.contacts = contacts
        self.connections_queue_size = connections_queue_size
        self.notify_interval = notify_interval
            
        self.meessages_queue = collections.deque()

        self.message_consumers = []

        self.kill_flag = False

        threading.Thread(target=self.__start_listening).start()

        threading.Thread(target=self.__start_notifying).start()


    def register_consumer(self, message_consumer: MessageConsumer):
        """
        Registers a message_consumer.
        message_consumer: message_consumer to register as a listener
        """
        self.message_consumers.append(message_consumer)


    def __start_notifying(self):
        """
        Starts periodically decrypting and verifying messages, and notified the registered message consumers.
        """

        while True:

            if len(self.meessages_queue) > 0:

                while len(self.meessages_queue) > 0:
                    try:

                        encrypted_pickled_message, signature, sender_id = self.meessages_queue.popleft()
                        sender_public_key = self.__get_contact_public_key(sender_id)
                        
                        rsa.verify(encrypted_pickled_message, signature, sender_public_key)

                        pickled_message = rsa.decrypt(encrypted_pickled_message, self.private_key)

                        message = pickle.loads(pickled_message)

                        self.__notify_consumers(message, sender_id)

                    except:

                        continue


            time.sleep(self.notify_interval)

    def __get_contact_public_key(self, contact_id: str):

        for contact in self.contacts:
            
            if contact.id == contact_id:

                return contact.public_key

        raise Exception()

    def kill(self):

        self.kill_flag = True


    def __start_listening(self):
        """
        Starts listening for incoming connections.
        """

        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('', self.port))
        s.listen(self.connections_queue_size)
        
        while not self.kill_flag:
        
            connection, addr = s.accept()

            if self.kill_flag:

                break
            
            try:
                # Receiving sender contact id
                sender_id = connection.recv(74).decode('utf-8')
                connection.send(b'\xff')

                # Receiving size of message
                message_length = int(connection.recv(4).decode('utf-8'))
                connection.send(b'\xff')

                # Receiving signature
                signature = connection.recv(64)
                connection.send(b'\xff')

                # Receiving message
                encrypted_pickled_message = connection.recv(message_length)
                
                connection.close()
                
                self.meessages_queue.append((encrypted_pickled_message, signature, sender_id))

            except:

                continue


    def __notify_consumers(self, message, sender_id):
        """
        Notifies all registered message consumers.
        """

        for consumer in self.message_consumers:
            
            consumer.notify(message, sender_id)

    
if __name__ == '__main__':

    sender_pub, sender_priv = rsa.newkeys(512)
    receiver_pub, receiver_priv = rsa.newkeys(512)

    receiver_contact = Contact(
        'receiver',
        '127.0.0.1',
        8000,
        receiver_pub
    )

    sender_contact = Contact(
        'sender',
        '127.0.0.1',
        8001,
        sender_pub
    )

    receiver = MessageReceiver(
        receiver_contact.port,
        receiver_priv,
        [sender_contact]
    )

    class Printer(MessageConsumer):

        def notify(self, message, sender_id):

            print("Received message from " + sender_id + ": " + message)

    receiver.register_consumer(Printer())

    sender = MessageSender(receiver_contact)

    sender.send_message("Ciao", sender_contact.id, sender_priv)
