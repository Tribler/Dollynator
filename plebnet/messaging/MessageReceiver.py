import socket
import collections
import threading
import time
import pickle

from MessageConsumer import MessageConsumer

from interface import Interface

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

        threading.Thread(target=self.__startListening).start()

        threading.Thread(target=self.__startNotifying).start()


    def registerConsumer(self, messageConsumer: MessageConsumer):
        """
        Registers a MessageConsumer.
        """
        self.messageConsumers.append(messageConsumer)


    def __startNotifying(self):

        while True:
            
            if len(self.messagesQueue) > 0:

                self.__notifyConsumers(pickle.loads(self.messagesQueue.popleft()))
                
            time.sleep(self.notifyInterval)



    def __startListening(self):
    
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

    def __notifyConsumers(self, message):
        
        for consumer in self.messageConsumers:
            
            consumer.notify(message)
