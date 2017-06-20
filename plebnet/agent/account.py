
class Account(object):
    """
    Account serves as a datastructure for all account details related to the agent.
    """

    def __init__(self):

        # Identity
        self.first_name = None
        self.last_name = None
        self.email = None

        # Whereabouts
        self.city = None
        self.state = None
        self.postcode = None
        self.phonenumber = None

        # Login details
        self.accountname = None
        self.password = None

        # Recovery options

