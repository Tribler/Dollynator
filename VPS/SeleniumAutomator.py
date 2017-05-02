from random import randint

from selenium import webdriver
from selenium.webdriver.support.select import Select

from Generator import Generator


class SeleniumAutomator(object):
    def __init__(self):
        self.driver = None
        self.generator = Generator()

    def spawn_browser(self):
        """Spawns the browser"""
        self.driver = webdriver.Chrome()

    def fill_in_element(self, css_selector, value):
        """
        Automatically fills ina form element by executing a piece of javascript that sets the value attribute of the 
        form element
        """
        element = self.driver.find_element_by_css_selector(css_selector)
        element.click()
        element.send_keys(value)

    def click_random_select_element(self, css_selector):
        """
        Chooses one of the elements in a select list randomly, except for the first element.
        """
        el = self.driver.find_element_by_css_selector(css_selector)
        options = el.find_elements_by_tag_name('option')
        num = randint(1, len(options) - 1)
        option = options[num]
        option.click()

    def click_select_element(self, css_selector, value):
        """
        Chooses one the element in a select list that has value 'value', or return false
        """
        el = self.driver.find_element_by_css_selector(css_selector)
        options = el.find_elements_by_tag_name('option')
        for option in options:
            if option.get_attribute('value') == value:
                option.click()
                return True
        return False

    def choose_select_element(self, css_selector, field_text):
        """
        Chooses one of the elements in a select list, by its visible text
        """
        select = Select(self.driver.find_element_by_css_selector(css_selector))
        # select.deselect_all()
        select.select_by_visible_text(field_text)

    def close_browser(self):
        """Closes the current browser instance of Selenium."""
        self.driver.quit()
