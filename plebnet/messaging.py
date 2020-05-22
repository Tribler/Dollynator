import pickle
import socket
import collections
import threading
import time

from abc import ABC


class MessageSender:
    """
    Class for sending messages to MessageReceivers.
    """

    def __init__(self, host: str, port: int):
        """
        host: Receipient host name.
        port: Receipient port
        """
        self.port = port
        self.host = host

    def send_message(self, data):
        """
        Sends a message.
        data: message payload
        """

        meessage_body = pickle.dumps(data)

        s = socket.socket()

        s.connect((self.host, self.port))

        s.send(str(len(meessage_body)).encode('utf-8'))

        s.recv(1)

        s.send(meessage_body)



        s.close()


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

    def __init__(self, port, connections_queue_size=20, notify_interval=1):

        self.port = port
        # TODO : make queue dynamically able to grow
        self.connections_queue_size = connections_queue_size
        self.notify_interval = notify_interval

        self.messages_queue = collections.deque()

        self.message_consumers = {
            'network' : [],
            'learning' : []
        }
        self.router = Router()

        threading.Thread(target=self.__start_listening).start()

        # threading.Thread(target=self.__start_notifying).start()

    def register_consumer(self, message_consumer, list):
        """
        Registers a message_consumer.
        message_consumer: message_consumer to register as a listener
        """
        self.message_consumers[list].append(message_consumer)

    def __start_notifying(self):
        """
        Starts periodically notifying the registered message consumers.
        """
        while True:

            for i in self.router.queues:
                if len(self.router.queues[i]) > 0:
                    self.__notify_consumers(i)




            #if len(self.meessages_queue) > 0:
            #   self.__notify_consumers(pickle.loads(self.meessages_queue.popleft()))

            time.sleep(self.notify_interval)

    def __start_listening(self):
        """
        Starts listening for incoming connections.
        """
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        s.bind(('', self.port))

        s.listen(self.connections_queue_size)

        while True:
            connection, addr = s.accept()

            message_length = int(connection.recv(4).decode('utf-8'))

            connection.send(b'\xff')

            message = connection.recv(message_length)

            connection.close()


            #self.messages_queue.append(message)
            self.router.routing(message)

    def __notify_consumers(self, key):
        """
        Notifies all registered message consumers.
        """
        for consumer in self.message_consumers[key]:
            consumer.notify(self.router.queues[key].popleft())

class Router:

    def __init__(self):

        self.queues = {

            'network': collections.deque(),
            'learning': collections.deque()

        }

    def _parse_message(self, raw_message):
            """
            Parses a raw message into command and data.
            raw_message: raw_message to parse
            """
            msg = pickle.loads(raw_message)
            command = msg['command']
            data = msg['data']

            print(data)

            return msg, command, data

    # TODO: SHALL WE MAKE IT MORE FLEXIBLE?
    def routing(self, message):

        msg, command, data = self._parse_message(message)

        if command == 'add-contact':
            self.queues['network'].append(msg)


        if command == 'qtable':
            self.queues['learning'].append(msg)






# Receives messages
def __demo_receive(port):
    # Initialize the message receiver service
    receiver = MessageReceiver(port)

    # Declare message consumers
    class Consumer:

        def notify(self, message):
            print(message)

    consumer1 = Consumer()
    consumer2 = Consumer()

    # Register the consumers
    receiver.register_consumer(consumer1, 'learning')
    receiver.register_consumer(consumer2, 'network')


# Sends messages
def __demo_send(sleepTime, port, host='127.0.0.1'):
    # Initialize sender
    sender = MessageSender(host, port)
    print()
    # Send message
    counter = 0

    while True:
        time.sleep(sleepTime)

        msg1 = {
            'command': 'add-contact',
            'data': 'this message is for network purposes'
        }

        msg2 = {
            'command': 'add-contact',
            'data': 'this message is for learning purposes'
        }

        sender.send_message(msg1)
        sender.send_message(msg2)
        counter += 1


if __name__ == '__main__':
    port = 8001

    # Start sender and receiver on two separate threads
    threading.Thread(target=__demo_send, args=(1, port,)).start()
    threading.Thread(target=__demo_receive, args=(port,)).start()

