import unittest
import time
from plebnet.messaging import Contact
from plebnet.messaging import Message
from plebnet.messaging import MessageConsumer
from plebnet.messaging import MessageReceiver
from plebnet.messaging import MessageSender
from plebnet.messaging import MessageDeliveryError
from plebnet.messaging import generate_contact_key_pair


class DebugConsumer(MessageConsumer):

    def __init__(self):

        self.messages = []

    def notify(self, message: Message, sender_id) -> None:

        self.messages.append((sender_id, message))


class TestMessaging(unittest.TestCase):

    port_range_min = 8000
    notify_interval = 0.01
    localhost = "127.0.0.1"

    def assert_and_kill_receiver(self, assertions, receiver: MessageReceiver):

        try:

            assertions()

        except AssertionError as e:

            self.fail(e)

        finally:

            receiver.kill()

    def test_messaging_single_channel(self) -> None:
        """
        Basic messaging test.
        """

        receiver_public, receiver_private = generate_contact_key_pair()
        sender_public, sender_private = generate_contact_key_pair()

        sender_contact = Contact(
            id="sender",
            public_key=sender_public,
            host=self.localhost,
            port=self.port_range_min
        )

        receiver_contact = Contact(
            id="receiver",
            public_key=receiver_public,
            host=self.localhost,
            port=self.port_range_min
        )

        channel = "channel1"

        sender = MessageSender(receiver_contact)

        consumer = DebugConsumer()

        receiver = MessageReceiver(
            port=self.port_range_min,
            private_key=receiver_private,
            contacts=[sender_contact],
            notify_interval=self.notify_interval
        )
        receiver.register_consumer(channel, consumer)

        message = Message(channel, "test command", "test data")

        sender.send_message(
            message=message,
            sender_contact_id=sender_contact.id,
            private_key=sender_private
        )

        time.sleep(self.notify_interval * 2)

        def assertions():

            assert len(consumer.messages) == 1

            received_message_sender_id, received_message = consumer.messages[0]

            assert received_message_sender_id == sender_contact.id
            assert received_message == message

        self.assert_and_kill_receiver(assertions, receiver)


    def test_messaging_multiple_channels(self):

        """
        Messaging test with multiple channels.
        """

        receiver_public, receiver_private = generate_contact_key_pair()
        sender_public, sender_private = generate_contact_key_pair()

        sender_contact = Contact(
            id="sender",
            public_key=sender_public,
            host=self.localhost,
            port=self.port_range_min
        )

        receiver_contact = Contact(
            id="receiver",
            public_key=receiver_public,
            host=self.localhost,
            port=self.port_range_min
        )

        channel1 = "channel1"
        channel2 = "channel2"

        sender = MessageSender(receiver_contact)

        consumer1 = DebugConsumer()
        consumer2 = DebugConsumer()

        receiver = MessageReceiver(
            port=self.port_range_min,
            private_key=receiver_private,
            contacts=[sender_contact],
            notify_interval=self.notify_interval
        )
        receiver.register_consumer(channel1, consumer1)
        receiver.register_consumer(channel2, consumer2)

        message1 = Message(channel1, "test command", "message 1")
        message2 = Message(channel2, "test command", "message 2")

        sender.send_message(
            message=message1,
            sender_contact_id=sender_contact.id,
            private_key=sender_private
        )

        sender.send_message(
            message=message2,
            sender_contact_id=sender_contact.id,
            private_key=sender_private
        )

        time.sleep(self.notify_interval * 2)

        def assertions():

            assert len(consumer1.messages) == 1
            assert len(consumer2.messages) == 1

            received_message_sender_id1, received_message1 = consumer1.messages[0]
            received_message_sender_id2, received_message2 = consumer2.messages[0]

            assert received_message_sender_id1 == sender_contact.id
            assert received_message_sender_id2 == sender_contact.id
            assert received_message1 == message1
            assert received_message2 == message2

        self.assert_and_kill_receiver(assertions, receiver)

    def test_kill_receiver(self):
        """
        Tests that a receiver can be open and appropriately killed.
        """
        pub, priv = generate_contact_key_pair()

        receiver = MessageReceiver(
            self.port_range_min,
            private_key=priv,
            contacts=[]
        )

        time.sleep(0.1)

        receiver.kill()

    def test_wrong_sender_private(self):
        """
        Tests that sending message with wrong key results in MessageDeliveryError.
        """

        receiver_public, receiver_private = generate_contact_key_pair()
        sender_public, sender_private = generate_contact_key_pair()

        wrong_public, wrong_private = generate_contact_key_pair()

        sender_contact = Contact(
            id="sender",
            public_key=sender_public,
            host=self.localhost,
            port=self.port_range_min
        )

        receiver_contact = Contact(
            id="receiver",
            public_key=receiver_public,
            host=self.localhost,
            port=self.port_range_min
        )

        channel = "channel1"

        sender = MessageSender(receiver_contact)

        consumer = DebugConsumer()


        receiver = MessageReceiver(
            port=self.port_range_min,
            private_key=receiver_private,
            contacts=[sender_contact],
            notify_interval=self.notify_interval
        )
        receiver.register_consumer(channel, consumer)

        message = Message(channel, "test command", "test data")

        sender.send_message(
            message=message,
            sender_contact_id=sender_contact.id,
            private_key=wrong_private
        )

        time.sleep(self.notify_interval * 2)

        def assertions():

            assert len(consumer.messages) == 0

        self.assert_and_kill_receiver(assertions, receiver)

    def test_wrong_receiver_public(self):
        """
        Tests that sending message with wrong key results in MessageDeliveryError.
        """

        receiver_public, receiver_private = generate_contact_key_pair()
        sender_public, sender_private = generate_contact_key_pair()

        wrong_public, wrong_private = generate_contact_key_pair()

        sender_contact = Contact(
            id="sender",
            public_key=sender_public,
            host=self.localhost,
            port=self.port_range_min
        )

        receiver_contact = Contact(
            id="receiver",
            public_key=wrong_public,
            host=self.localhost,
            port=self.port_range_min
        )

        channel = "channel1"

        sender = MessageSender(receiver_contact)

        consumer = DebugConsumer()

        receiver = MessageReceiver(
            port=self.port_range_min,
            private_key=receiver_private,
            contacts=[sender_contact],
            notify_interval=self.notify_interval
        )
        receiver.register_consumer(channel, consumer)

        message = Message(channel, "test command", "test data")

        sender.send_message(
            message=message,
            sender_contact_id=sender_contact.id,
            private_key=sender_private
        )

        time.sleep(self.notify_interval * 2)

        def assertions():

            assert len(consumer.messages) == 0

        self.assert_and_kill_receiver(assertions, receiver)


if __name__ == 'main':
    unittest.main()
