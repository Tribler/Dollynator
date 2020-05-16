from plebnet.contacts.AddressBook import AddressBook
from plebnet.contacts.Contact import Contact, generate_contact_id
import random
import time

port_counter = 8000
root_id = generate_contact_id("")
root_contact = Contact(root_id, '127.0.0.1', port_counter)

nodes = [AddressBook(root_contact)]

port_counter += 1

while True:

    replicating_node = nodes[random.randint(0, len(nodes) - 1)]

    new_node_contact = Contact(generate_contact_id(replicating_node.self_contact.id), '127.0.0.1', port_counter)
    new_node = AddressBook(new_node_contact, replicating_node.contacts)

    nodes.append(new_node)

    replicating_node.create_new_distributed_contact(new_node.self_contact)
    port_counter += 1

    time.sleep(1)
