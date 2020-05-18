import pickle
import socket
import collections
import threading
import time

from abc import ABC


class MessageSender:
    
    def __init__(self, host: str, port: int):

        self.port = port
        self.host = host
        

    def send_message(self, data):
 
        messageBody = pickle.dumps(data)

        s = socket.socket()   
               
        s.connect((self.host, self.port)) 

        s.send(str(len(messageBody)).encode('utf-8'))

        s.recv(1)

        s.send(messageBody)

        s.close()



class MessageReceiver:
    """
    Message receiving service. Opens a socket on the specified port, and notifies
    registered consumers when new messages are received.
    """

    def __init__(self, port, connectionsQueueSize = 20, notifyInterfal = 1):

        self.port = port
        self.connectionsQueueSize = connectionsQueueSize
        self.notifyInterval = notifyInterfal

        self.messagesQueue = collections.deque()

        self.messageConsumers = []

        threading.Thread(target=self.__start_listening).start()

        threading.Thread(target=self.__start_notifying).start()


    def register_consumer(self, messageConsumer):
        """
        Registers a MessageConsumer.
        """
        self.messageConsumers.append(messageConsumer)


    def __start_notifying(self):

        while True:
            
            if len(self.messagesQueue) > 0:

                self.__notify_consumers(pickle.loads(self.messagesQueue.popleft()))
                
            time.sleep(self.notifyInterval)



    def __start_listening(self):
    
        s = socket.socket()           
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        s.bind(('', self.port))
        
        s.listen(self.connectionsQueueSize)
        
        while True: 
        
            connection, addr = s.accept()
            
            messageLength = int(connection.recv(4).decode('utf-8'))

            connection.send(b'\xff')

            message = connection.recv(messageLength)
            
            connection.close() 

            self.messagesQueue.append(message)


    def __notify_consumers(self, message):
        
        for consumer in self.messageConsumers:
            
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
