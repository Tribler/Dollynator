from MessageConsumer import MessageConsumer
from MessageReceiver import MessageReceiver
from MessageSender import MessageSender

from interface import implements

import threading
import time
import pickle 

# Receives messages
def receive(port):

    # Initialize the message receiver service
    receiver = MessageReceiver(port)
    
    # Declare message consumers
    class Consumer(implements(MessageConsumer)):

        def notify(self, message): 

            print(message)

    consumer1 = Consumer()
    consumer2 = Consumer()

    # Register the consumers
    receiver.registerConsumer(consumer1)
    receiver.registerConsumer(consumer2)

# Sends messages
def send(sleepTime, port, host='127.0.0.1'):
    
    # Initialize sender
    sender = MessageSender(port)
    
    # Send message
    counter = 0
    
    while True:
        
        time.sleep(sleepTime)

        sender.sendMessage(host, "Counter: " + str(counter))
        counter += 1

if __name__ == '__main__':
    port = 8000

    # Start sender and receiver on two separate threads
    threading.Thread(target=send, args= (1, port,)).start()
    threading.Thread(target=receive, args = (port,)).start()

