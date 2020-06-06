from plebnet.messaging import Message, Contact, MessageConsumer, generate_contact_key_pair
from plebnet.address_book import AddressBook
import random
import threading
import time


def log(node, message):

    print("Node " + node.self_contact.id + ": " + message)


def demo():
    
    global nodes
    nodes = []

    def start_replicating(
        ports_range = 8000,
        replicating_interval = 1,
        ping_interval = 1,
        restore_timeout = 2,
        receiver_notify_interval = 0.001
    ):

        id_counter = 1

        root_pub, root_priv = generate_contact_key_pair()
        root_contact = Contact(
            id=str(id_counter),
            host="127.0.0.1",
            port=ports_range,
            public_key=root_pub
        )

        root = AddressBook(
            self_contact=root_contact,
            private_key=root_priv,
            contact_restore_timeout=restore_timeout,
            inactive_nodes_ping_interval=ping_interval,
            receiver_notify_interval=receiver_notify_interval
        )

        global nodes
        nodes.append(root)

        while True:

            ports_range += 1
            id_counter += 1

            replicating_node = random.choice(nodes)

            log(replicating_node, "Replicating")

            new_node_contact_list = replicating_node.contacts.copy()
            new_node_contact_list.append(replicating_node.self_contact)

            pub, priv = generate_contact_key_pair()

            new_node_contact = Contact(
                id=str(id_counter),
                host='127.0.0.1',
                port=ports_range,
                public_key=pub
            )

            new_node = AddressBook(
                self_contact=new_node_contact,
                private_key=priv,
                contacts=new_node_contact_list,
                contact_restore_timeout=restore_timeout,
                inactive_nodes_ping_interval=ping_interval,
                receiver_notify_interval=receiver_notify_interval
            )

            nodes.append(new_node)

            replicating_node.create_new_distributed_contact(new_node_contact)

            time.sleep(replicating_interval)

    def start_killing(
        nodes_threshold = 5,
        killing_interval = 2
    ):
        global nodes

        while True:

            time.sleep(killing_interval)

            if (len(nodes) < nodes_threshold):

                continue

            kill_probability = 1 / 6

            for node in nodes:

                if random.uniform(0, 1) <= kill_probability:

                    log(node, "dying")

                    node.kill()
                    nodes.remove(node)

    def print_snapshots(
        print_interval = 3
    ):

        global nodes

        while True:
            
            time.sleep(print_interval)

            print("\n=====================================================")

            for node in nodes:
                
                contacts_list = ""

                for contact in node.contacts:

                    contacts_list += str(contact.id) + ", "

                print("Node " + node.self_contact.id + " has " + str(len(node.contacts)) + " contacts: " + contacts_list)

            print("=====================================================\n")



    threading.Thread(target=start_replicating).start()
    threading.Thread(target=start_killing).start()
    threading.Thread(target=print_snapshots).start()


if __name__ == "__main__":
    demo()
