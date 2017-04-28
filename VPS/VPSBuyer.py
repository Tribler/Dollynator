from random import randint
from selenium import webdriver
from selenium.webdriver.support.select import Select

from Util import Util


class VPSBuyer(object):
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
        self.driver = None
        self.price = None
        self.generator = Util()
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

    def _spawn_browser(self):
        """Spawns the browser to use when internetting."""
        self.driver = webdriver.Chrome()
        # self.driver = webdriver.Remote(
        #     command_executor='http://127.0.0.1:4444/wd/hub',
        #     desired_capabilities=DesiredCapabilities.FIREFOX)

    def _fill_in_element(self, fieldname, value):
        """
        Automatically fills ina form element by executing a piece of javascript that sets the value attribute of the 
        form element
        """
        # driver.find_element_by_css_selector("input[name='" + fieldname + "']").send_keys(value)

        # ^ send_keys has some issues, using javascript to set an attribute instead:
        self.driver.find_element_by_name(fieldname)  # Selenium waits until this element exists
        self.driver.execute_script(
            'document.getElementsByName("' + fieldname + '")[0].setAttribute("value", "' + value + '")')

    def _click_random_select_element(self, field_id):
        """
        Chooses one of the elements in a select list randomly, except for the first element.
        """
        el = self.driver.find_element_by_id(field_id)
        options = el.find_elements_by_tag_name('option')
        num = randint(1, len(options) - 1)
        option = options[num]
        option.click()

    def _click_select_element(self, field_id, value):
        """
        Chooses one the element in a select list that has value 'value', or return false
        """
        el = self.driver.find_element_by_id(field_id)
        options = el.find_elements_by_tag_name('option')
        for option in options:
            if option.get_attribute('value') == value:
                option.click()
                return True
        return False

    def _choose_select_element(self, field_name, field_text):
        """
        Chooses one of the elements in a select list, by its visible text
        """
        select = Select(self.driver.find_element_by_name(field_name))
        # select.deselect_all()
        select.select_by_visible_text(field_text)

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

    def _close_browser(self):
        """Closes the current browser instance of Selenium."""
        self.driver.quit()
