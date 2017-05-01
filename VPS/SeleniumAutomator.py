from random import randint
from selenium import webdriver
from selenium.webdriver.support.select import Select

from Generator import Generator


class SeleniumAutomator(object):
    def __init__(self):
        pass
        self.generator = Generator()

    def _spawn_browser(self):
        """Spawns the browser to use when internetting."""
        self.driver = webdriver.Chrome()
        # self.driver = webdriver.Remote(
        #     command_executor='http://127.0.0.1:4444/wd/hub',
        #     desired_capabilities=DesiredCapabilities.FIREFOX)

    def _fill_in_element(self, css_selector, value):
        """
        Automatically fills ina form element by executing a piece of javascript that sets the value attribute of the 
        form element
        """
        element = self.driver.find_element_by_css_selector(css_selector)
        element.click()
        element.send_keys(value)

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

    def _close_browser(self):
        """Closes the current browser instance of Selenium."""
        self.driver.quit()
