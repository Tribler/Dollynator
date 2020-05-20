import pickle
import socket
import collections
import threading
import time


class MessageConsumer:

    def notify(self, message):

        pass


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
        

    def send_message(self, data, ack_timeout=5.0):
        """
        Sends a message.
        data: message payload
        """

        # Pickling message
        message_body = pickle.dumps(data)

        # Connecting to receiver
        s = socket.socket()
        s.connect((self.host, self.port)) 

        # Sending size of message
        s.send(str(len(message_body)).encode('utf-8'))

        # Waiting for ack
        s.settimeout(ack_timeout)
        s.recv(1)

        # Sending message
        s.send(message_body)

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

    def __init__(self, port, connections_queue_size = 20, notify_interval = 1):

        self.port = port
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
        Starts periodically notifying the registered message consumers.
        """
        while True:
            
            if len(self.meessages_queue) > 0:

                self.__notify_consumers(pickle.loads(self.meessages_queue.popleft()))
                
            time.sleep(self.notify_interval)


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
            
            message_length = int(connection.recv(4).decode('utf-8'))

            connection.send(b'\xff')

            message = connection.recv(message_length)
            
            connection.close()

            self.meessages_queue.append(message)


    def __notify_consumers(self, message):
        """
        Notifies all registered message consumers.
        """
        for consumer in self.message_consumers:
            
            consumer.notify(message)


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
    receiver.register_consumer(consumer1)
    receiver.register_consumer(consumer2)

# Sends messages
def __demo_send(sleepTime, port, host='127.0.0.1'):
    
    # Initialize sender
    sender = MessageSender(host, port)
    
    # Send message
    counter = 0
    
    while True:
        
        time.sleep(sleepTime)

        sender.send_message("Counter: " + str(counter))
        counter += 1

if __name__ == '__main__':

    port = 8000

    # Start sender and receiver on two separate threads
    threading.Thread(target=__demo_send, args= (1, port,)).start()
    threading.Thread(target=__demo_receive, args = (port,)).start()
