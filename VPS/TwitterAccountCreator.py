import time

from SeleniumAutomator import SeleniumAutomator


class TwitterAccountCreator(SeleniumAutomator):
    def __init__(self):
        SeleniumAutomator.__init__(self)

    def login(self, username, password):
        print("Logging in as " + username + ":" + password);
        self._spawn_browser()
        self.driver.get("https://twitter.com/")
        self._fill_in_element('#signin-email', username)
        self._fill_in_element('#signin-password', password)
        self.driver.find_element_by_css_selector("button.submit.btn.primary-btn.flex-table-btn.js-submit").click()

    def create(self):
        self._spawn_browser()
        self.driver.get("https://twitter.com/")
        time.sleep(1)
        self._fill_in_element('[name="user[name]"]', self.generator.get_first_name() + " " + self.generator.get_last_name())
        time.sleep(1)
        self._fill_in_element('[name="user[email]"]',
                              self.generator.get_first_name() + self.generator.get_last_name() + "Pleb@heijligers.me")
        time.sleep(1)
        self._fill_in_element('[name="user[user_password]"]', self.generator.get_password())
        time.sleep(1)
        print(self.generator.get_first_name(), self.generator.get_last_name(), self.generator.get_password())
        self.driver.find_element_by_css_selector(".btn.signup-btn.u-floatRight").click()
        time.sleep(1)
        self.driver.find_element_by_css_selector(".submit.button.signup").click()
        time.sleep(1)
        self.driver.get("https://twitter.com")
        time.sleep(1)
        self.driver.find_element_by_css_selector("#tweet-box-home-timeline > div").click()
        time.sleep(1)
        self.driver.find_element_by_css_selector("#tweet-box-home-timeline").send_keys(
            "@Pleb_Net A new pleb has arrived #PlebNet")
        time.sleep(1)
        self.driver.find_element_by_css_selector(
            "div.home-tweet-box.tweet-box.component.tweet-user > form.tweet-form > div.TweetBoxToolbar > div.TweetBoxToolbar-tweetButton.tweet-button > button.btn.primary-btn.tweet-action.tweet-btn.js-tweet-btn").click()
