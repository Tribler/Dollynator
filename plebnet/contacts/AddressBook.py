
from plebnet.messaging import MessageConsumer
from plebnet.messaging import MessageSender
from plebnet.messaging import MessageReceiver



from plebnet.contacts.Contact import Contact


# TODO: change package methods naming
# TODO: 

class AddressBook(MessageConsumer):

    def __init__(self, self_contact: Contact, contacts: list = [],):
        
        self.receiver = MessageReceiver(self_contact.port)
        
        self.contacts = contacts.copy()
        self.receiver.registerConsumer(self)
        self.self_contact = self_contact


    def parse_message(self, raw_message):

        command = raw_message['command']
        data = raw_message['data']

        return command, data


    def generate_add_contact_message(self, contact: Contact):

        return {
            'command': 'add-contact',
            'data': contact
        }


    def __add_contact(self, contact: Contact):

        for known_contact in self.contacts:

            if known_contact.id == contact.id:

                return

        self.contacts.append(contact)

        self.__forward_contact(contact)


    def __forward_contact(self, contact: Contact):
        
        message = self.generate_add_contact_message(contact)

        for known_contact in self.contacts:
            
            if known_contact.id == self.self_contact.id:
                continue 
            
            self.__send_message_to_contact(known_contact, message)
            

    def __send_message_to_contact(self, recipient: Contact, message):
        
        sender = MessageSender(recipient.host, recipient.port)

        sender.sendMessage(message)

    
    def notify(self, rawMessage):
        
        command, data = self.parse_message(rawMessage)

        if command == 'add-contact':

            self.__add_contact(data)


    def create_new_distributed_contact(self, contact: Contact):

        self.contacts.append(contact)

        message = self.generate_add_contact_message(contact)

        for known_contact in self.contacts[:-1]:

            self.__send_message_to_contact(known_contact, message)