from MessageConsumer import MessageConsumer
from MessageReceiver import MessageReceiver
from MessageSender import MessageSender

from interface import implements

import threading
import time
import pickle 

# Receives messages
def receive():

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
def send(sleepTime):
    
    # Initialize sender
    sender = MessageSender(port)
    
    # Send message
    counter = 0
    
    while True:
        
        time.sleep(sleepTime)

        sender.sendMessage("Counter: " + str(counter))
        counter += 1

# Start sender and receiver on two separate threads
port = 8000

threading.Thread(target=send, args= (1, )).start()
threading.Thread(target=receive).start()

