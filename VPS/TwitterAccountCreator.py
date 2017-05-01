import time

from SeleniumAutomator import SeleniumAutomator


class TwitterAccountCreator(SeleniumAutomator):
    def __init__(self):
        SeleniumAutomator.__init__(self)

    def create(self):
        self._spawn_browser()
        self.driver.get("https://twitter.com/")
        time.sleep(1)
        self._fill_in_element('user[name]', self.generator.get_first_name() + " " + self.generator.get_last_name())
        time.sleep(1)
        self._fill_in_element('user[email]',
                              self.generator.get_first_name() + self.generator.get_last_name() + "Pleb@heijligers.me")
        time.sleep(1)
        self._fill_in_element('user[user_password]', self.generator.get_password())
        time.sleep(1)
        print(self.generator.get_first_name(), self.generator.get_last_name(), self.generator.get_password())
        self.driver.find_element_by_css_selector(".btn.signup-btn.u-floatRight").click()
        time.sleep(1)
        self.driver.find_element_by_css_selector(".submit.button.signup").click()
        time.sleep(1)
        self.driver.get("https://twitter.com")
        time.sleep(1)
        self.driver.find_element_by_css_selector(".tweet-content").click()
        self.driver.find_element_by_css_selector(".tweet-content").send_keys(
            "@Pleb_Net A new pleb has arrived #PlebNet")
        time.sleep(1)
        self.driver.find_element_by_css_selector(
            ".btn.primary-btn.tweet-action.disabled.tweet-btn.js-tweet-btn").click()
