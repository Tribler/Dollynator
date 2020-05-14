import pickle
import socket

class MessageSender:

    def __init__(self, port: int):

        self.port = port
        

    def sendMessage(self, host: str, data):
 
        messageBody = pickle.dumps(data)

        s = socket.socket()   
               
        s.connect((host, self.port)) 

        s.send(str(len(messageBody)).encode('utf-8'))

        s.recv(1)

        s.send(messageBody)

        s.close()