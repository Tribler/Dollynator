from random import randrange
import random
import string


class Util:

    def __init__(self):
        pass

    def get_phone_num(self):
        """
        returns a 10 sized phone number
        """
        if hasattr(self, 'phoneNum'):
            return self.phoneNum

        self.phoneNum = self.get_random_numerical_string(10)
        return self.phoneNum

    def get_email(self):
        """
        returns a random email adress.

        This email adress is bogus and cannot be accessed.
        """
        if hasattr(self, 'email'):
            return self.email

        tlds = [".com", ".co.uk", ".eu", ".ch", ".org"]
        self.email = self.get_random_alphabetical_string(randrange(3, 10)) + "@" + self.get_random_alphabetical_string(
            randrange(3, 10)) + tlds[randrange(0, len(tlds))]
        return self.email

    def get_first_name(self):
        """ returns a bogus firstname. """
        if hasattr(self, 'firstName'):
            return self.firstName

        self.firstName = self.get_random_alphabetical_string(randrange(3, 10))
        return self.firstName

    def get_surname(self):
        """returns a bogus surname."""
        if hasattr(self, 'surname'):
            return self.surname

        self.surname = self.get_random_alphabetical_string(randrange(3, 10))
        return self.surname

    def get_city(self):
        """returns a bogus city."""
        if hasattr(self, 'city'):
            return self.city

        self.city = self.get_random_alphabetical_string(randrange(3, 10))
        return self.city

    def get_zipcode(self):
        """ returns a american zipcode. """
        if hasattr(self, 'zipcode'):
            return self.zipcode
        self.zipcode = self.get_random_numerical_string(5)
        return self.zipcode

    def get_password(self):
        """ generates a password, do store it yourself."""
        if hasattr(self, 'password'):
            return self.password
        self.password = self.get_random_string(randrange(15, 30))
        return self.password

    @staticmethod
    def get_random_alphabetical_string(length):
        """
        returns a random string with size length.

        The string contains just alphabetical characters.
        """
        result = ""
        for _ in range(0, length):
            result += random.choice(string.ascii_letters)
        return result

    @staticmethod
    def get_random_numerical_string(length):
        """returns a random numerical string with size length."""
        result = ""
        for _ in range(0, length):
            result += random.choice(string.digits)
        return result

    @staticmethod
    def get_random_string(length):
        """
        returns a random string with size length (numerical, alphabetical and some random other signs)
        """
        result = ""
        for _ in range(0, length):
            result += random.choice(string.printable)
        return result
