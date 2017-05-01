from Generator import Generator
from SeleniumAutomator import SeleniumAutomator


class VPSBuyer(SeleniumAutomator):
    """
    This is the standard class to buy a VPS host.
    By itself, it does nothing; this class is supposed to be extended by other
    classes, each for a specific VPS Provider.

    email -- The email address. (Default is '')
    password -- The password for the account on the site. (Default is '')
    SSHUsername -- The user for the SSH Connection. (Default is 'root')
    SSHPassword -- The password for ssh connections. (Default is '')
    """

    def __init__(self, email='', password='', ssh_username='root', ssh_password=''):
        SeleniumAutomator.__init__(self)
        self.price = None
        if email == "":
            self.email = self.generator.get_email()
        else:
            self.email = email
        if password == "":
            self.password = self.generator.get_random_alphabetical_string(32)
        else:
            self.password = password
        self.SSHUsername = ssh_username

        self.SSHPassword = ssh_password
        if self.SSHPassword == "":
            self.SSHPassword = self.generator.get_random_alphabetical_string(32)
        self.IP = ""

    def buy(self):
        raise NotImplementedError

    def get_ssh_username(self):
        """Returns the SSH Username to log in on the bought VPS."""
        return self.SSHUsername

    def get_ssh_password(self):
        """Returns the SSH Password to log in on the bought VPS."""
        return self.SSHPassword

    def get_ip(self):
        """Returns the IP Address that the VPS is installed on."""
        return self.IP

    def get_email(self):
        """Returns the email address to log in on the VPS provider."""
        return self.email

    def get_password(self):
        """Returns the password to log in on the VPS provider."""
        return self.password

    def get_price(self):
        return self.price
