import pickle
import socket

class MessageSender:

    def __init__(self, port):

        self.port = port
        

    def sendMessage(self, data):
 
        messageBody = pickle.dumps(data)

        s = socket.socket()   
               
        s.connect(('127.0.0.1', self.port)) 

        s.send(str(len(messageBody)).encode('utf-8'))

        s.recv(1)

        s.send(messageBody)

        s.close()