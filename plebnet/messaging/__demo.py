from MessageConsumer import MessageConsumer
from MessageReceiver import MessageReceiver
from MessageSender import MessageSender

from interface import implements

import threading
import time
import pickle 

port = 8082

def server():

    receiver = MessageReceiver(port)
    
    class Consumer(implements(MessageConsumer)):

        def notify(self, message): 

            print(message)

    consumer1 = Consumer()
    consumer2 = Consumer()

    receiver.registerConsumer(consumer1)
    receiver.registerConsumer(consumer2)

def client(sleepTime):
    
    sender = MessageSender(port)
    
    counter = 0
    
    while True:
        
        time.sleep(sleepTime)

        sender.sendMessage(counter)
        counter += 1


threading.Thread(target=client, args= (1, )).start()
threading.Thread(target=server).start()

