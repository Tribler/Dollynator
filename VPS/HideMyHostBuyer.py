from VPSBuyer import VPSBuyer


class HideMyHostBuyer(VPSBuyer):
    def __init__(self):
        super(HideMyHostBuyer, self).__init__()

    def buy(self):
        self._spawn_browser()
        self.driver.get("http://www.hidemyhost.com/vps-hosting.php")
        self.driver.find_element_by_css_selector(
            "div.table-container > div:nth-of-type(2) > ul > li.orderbuttonspacing > a.medium").click()
        self._fill_in_element('[name="hostname"]', self.generator.get_first_name())
        self._fill_in_element('tbody > tr:nth-of-type(2) > td.fieldarea > input', self.generator.get_first_name())
        self._fill_in_element('tbody > tr:nth-of-type(3) > td.fieldarea > input', self.generator.get_first_name())
        self._fill_in_element('[name="rootpw"]', self.generator.get_password())
        self._choose_select_element("tbody > tr:first-child > td.fieldarea > select", "Ubuntu 14.04 64bit")
        self.driver.find_element_by_css_selector("input.checkout").click()
        self.driver.implicitly_wait(1)
        self._fill_in_element('[name="firstname"]', self.generator.get_first_name())
        self._fill_in_element('[name="lastname"]', self.generator.get_last_name())
        self._fill_in_element('[name="email"]', self.generator.get_email())
        self._fill_in_element('tbody > tr:nth-of-type(5) > td:nth-of-type(2) > input',
                              self.generator.get_random_alphabetical_string(10))
        self._fill_in_element('[name="city"]', self.generator.get_city())
        self._fill_in_element('#stateinput', self.generator.get_random_alphabetical_string(5))
        self._fill_in_element('[name="postcode"]', self.generator.get_random_numerical_string(5))
        self._fill_in_element('[name="phonenumber"]', self.generator.get_random_numerical_string(10))
        self._fill_in_element('#newpw', self.generator.get_password())
        self._fill_in_element('tbody > tr:nth-of-type(13) > td:nth-of-type(2) > input', self.generator.get_password())
        self.driver.find_element_by_css_selector("#accepttos").click()
        self.driver.find_element_by_css_selector(
            "input.cartbutton.green.ui-button.ui-widget.ui-state-default.ui-corner-all").click()
        self.driver.find_element_by_css_selector(
            "tr > td:nth-of-type(2) > form:nth-of-type(2) > input:nth-of-type(14)").click()
        amount = float(self.driver.find_element_by_css_selector("#coinAmountField > span").text)
        address = self.driver.find_element_by_css_selector("#paymentAddress").text
        print("Pay", amount, "to", address)
        self._close_browser()
