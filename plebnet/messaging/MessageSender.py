import pickle
import socket

class MessageSender:

    def __init__(self, host: str, port: int):

        self.port = port
        self.host = host
        

    def sendMessage(self, data):
 
        messageBody = pickle.dumps(data)

        s = socket.socket()   
               
        s.connect((self.host, self.port)) 

        s.send(str(len(messageBody)).encode('utf-8'))

        s.recv(1)

        s.send(messageBody)

        s.close()