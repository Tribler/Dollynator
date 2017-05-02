from VPSBuyer import VPSBuyer


class CrowncloudBuyer(VPSBuyer):
    def __init__(self):
        super(CrowncloudBuyer, self).__init__()

    def buy(self):
        self.spawn_browser()
        self.driver.get("https://crowncloud.net/")
        self.driver.find_element_by_css_selector("#navbar > ul:nth-of-type(1) > li:nth-of-type(2) > a").click()
        self.driver.find_element_by_css_selector(
            "div.container > div:nth-of-type(4) > div.table-responsive > table.table.table-striped > tbody > tr:nth-of-type(2) > td:nth-of-type(10) > a:nth-of-type(1)").click()
        self.choose_select_element("tbody > tr:first-child > td.fieldarea > select.form-control", "Ubuntu 16.04 64bit")
        self.driver.find_element_by_css_selector("#btnCompleteProductConfig").click()
        self.driver.implicitly_wait(3)
        self.fill_in_element('#firstname', self.generator.get_first_name())
        self.fill_in_element('#lastname', self.generator.get_last_name())
        self.fill_in_element('#email', self.generator.get_email())
        self.fill_in_element('div.row > div:nth-of-type(1) > div:nth-of-type(5) > input.form-control',
                             self.generator.get_password())
        self.fill_in_element('#inputNewPassword2',
                             self.generator.get_password())
        self.fill_in_element('div.row > div:nth-of-type(2) > div:nth-of-type(1) > input.form-control',
                             self.generator.get_random_alphabetical_string(10))
        self.fill_in_element('#city', self.generator.get_random_alphabetical_string(10))
        self.fill_in_element('#postcode', self.generator.get_zipcode())
        self.fill_in_element('#phonenumber', self.generator.get_phone_num())
        self.click_random_select_element("#stateselect")
        self.driver.find_element_by_css_selector("div.signupfields.padded > label:nth-of-type(2)").click()
        self.driver.find_element_by_css_selector("#frmCheckout > div:nth-of-type(9) > label.checkbox-inline").click()
        self.driver.find_element_by_css_selector("#btnCompleteOrder").click()
        self.driver.implicitly_wait(5)
        self.click_select_element('[name="gateway"]', "Bit-pay (Bitcoin)")
        self.driver.implicitly_wait(5)
        self.driver.find_element_by_css_selector("form > input:nth-of-type(11)").click()
        # self._close_browser()
