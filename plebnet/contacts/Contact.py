import hashlib
import random
import string
import calendar
import time


def generate_contact_id(parent_id: str):

    def generate_random_string(length):

        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(length))

    return str(hashlib.sha256((parent_id + generate_random_string(5)).encode('utf-8'))) + str(calendar.timegm(time.gmtime()))


class Contact:

    def __init__(self, id: str, host: str, port: int):
        
        self.id = id
        self.host = host
        self.port = port

    