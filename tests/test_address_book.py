import unittest

from plebnet.address_book import AddressBook
from plebnet.messaging import Contact
from plebnet.messaging import generate_contact_key_pair
from plebnet.messaging import generate_contact_id
from plebnet.messaging import Message
import random
import time


class TestAddressBook(unittest.TestCase):

    port_range_min = 8000
    receiver_notify_interval = 0.05
    inactive_nodes_ping_interval = 0.33
    contact_restore_timeout = inactive_nodes_ping_interval * 2 + 0.01
    replication_interval = 0.1

    def new_node(self, port: int, parent_ab: AddressBook = None) -> AddressBook:

        new_node_pub, new_node_priv = generate_contact_key_pair()

        parent_id = "" if parent_ab is None else parent_ab.self_contact.id
        contacts = [] if parent_ab is None else parent_ab.contacts + [parent_ab.self_contact]

        new_node_contact = Contact(
            host="127.0.0.1",
            id=generate_contact_id(parent_id),
            port=port,
            public_key=new_node_pub
        )

        new_node_ab = AddressBook(
            self_contact=new_node_contact,
            private_key=new_node_priv,
            contacts=contacts,
            receiver_notify_interval=self.receiver_notify_interval,
            contact_restore_timeout=self.contact_restore_timeout,
            inactive_nodes_ping_interval=self.inactive_nodes_ping_interval,
        )

        if parent_ab is not None:

            parent_ab.create_new_distributed_contact(new_node_contact)

        return new_node_ab

    def test_node_replication(self):

        port_counter = self.port_range_min

        root_ab = self.new_node(port_counter)

        nodes = [root_ab]

        replications = 10

        try:
            for i in range(replications):

                port_counter += 1

                replicating_node = random.choice(nodes)

                nodes.append(self.new_node(port_counter, replicating_node))

                time.sleep(self.replication_interval)

                for node in nodes:

                    assert len(node.contacts) == i + 1

        finally:

            for node in nodes:
                try:
                    node.kill()
                except:
                    continue

    def test_contact_removal_unexpected_death(self):

        nodes = []

        try:

            nodes.append(self.new_node(self.port_range_min))

            nodes.append(self.new_node(self.port_range_min + 1, nodes[0]))

            time.sleep(self.receiver_notify_interval * 2)

            for node in nodes:

                assert len(node.contacts) == 1

            nodes[0].kill()
            nodes[1].send_message_to_contact(nodes[0].self_contact, Message(
                channel="test",
                command="test"
            ))

            time.sleep(self.contact_restore_timeout * 2)

            assert len(nodes[1].contacts) == 0

        finally:

            for node in nodes:
                try:
                    node.kill()
                except:
                    continue

    def test_link_down_and_up(self):

        nodes = []

        try:

            nodes.append(self.new_node(self.port_range_min))

            nodes.append(self.new_node(self.port_range_min + 1, nodes[0]))

            time.sleep(self.receiver_notify_interval * 2)

            for node in nodes:

                assert len(node.contacts) == 1

            nodes[1].kill()

            nodes[0].send_message_to_contact(nodes[1].self_contact, Message(
                channel="test",
                command="test"
            ))

            assert not nodes[0].contacts[0].is_active()

            nodes[1] = AddressBook(
                self_contact=nodes[1].self_contact,
                private_key=nodes[1]._private_key,
                contacts=nodes[1].contacts,
                receiver_notify_interval=nodes[1].receiver.notify_interval,
                contact_restore_timeout=nodes[1]._contact_restore_timeout,
                inactive_nodes_ping_interval=nodes[1]._inactive_nodes_ping_interval
            )

            time.sleep(self.inactive_nodes_ping_interval * 1.5)

            assert nodes[0].contacts[0].is_active()

        finally:

            for node in nodes:
                try:
                    node.kill()
                except:
                    continue


if __name__ == 'main':
    unittest.main()
