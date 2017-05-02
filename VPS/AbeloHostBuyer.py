import time

from VPSBuyer import VPSBuyer


class AbeloHostBuyer(VPSBuyer):
    def __init__(self):
        super(AbeloHostBuyer, self).__init__()

    def buy(self):
        self.spawn_browser()
        self.driver.get("https://abelohost.com/offshore-vps/")
        self.driver.find_element_by_css_selector("#cookie_action_close_header").click()
        time.sleep(1)
        self.driver.find_element_by_css_selector(
            "div.wpb_content_element.button > a.btn-bt.align-center.default").click()
        self.driver.find_element_by_css_selector("div.form-group > label:nth-of-type(7)").click()
        self.driver.find_element_by_css_selector("div.panel-body > label").click()
        self.driver.find_element_by_css_selector("#btnCompleteProductConfig").click()
        time.sleep(3)
        self.fill_in_element("#firstname", self.generator.get_first_name())
        self.fill_in_element("#lastname", self.generator.get_last_name())
        self.fill_in_element("#email", self.generator.get_email())
        self.fill_in_element("div.row > div:nth-of-type(1) > div:nth-of-type(5) > input.form-control",
                             self.generator.get_password())
        self.fill_in_element("div.row > div:nth-of-type(1) > div:nth-of-type(6) > input.form-control",
                             self.generator.get_password())
        self.fill_in_element("div.row > div:nth-of-type(2) > div:nth-of-type(1) > input.form-control",
                             self.generator.get_random_alphabetical_string(10))
        self.fill_in_element("#city", self.generator.get_random_alphabetical_string(10))
        self.click_random_select_element("#stateselect")
        self.fill_in_element("#postcode", self.generator.get_zipcode())
        self.click_random_select_element("#country")
        self.fill_in_element("#phonenumber", self.generator.get_phone_num())
        self.fill_in_element("#securityqans", self.generator.get_random_alphabetical_string(10))
        self.driver.find_element_by_css_selector("div.signupfields.padded > label:nth-of-type(4)").click()
        self.driver.find_element_by_css_selector("#mainfrm > div:nth-of-type(11) > label.checkbox-inline").click()
        self.driver.find_element_by_css_selector("#btnCompleteOrder").click()
