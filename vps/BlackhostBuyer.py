from VPSBuyer import VPSBuyer


class BlackhostBuyer(VPSBuyer):
    def __init__(self):
        super(BlackhostBuyer, self).__init__()

    def register(self):
        self.spawn_browser()
        self.driver.get("https://black.host/unmetered-vps-hosting")
        self.driver.find_element_by_css_selector(".servers ul.red li .info .noline a").click()
        self.fill_in_element('[name="hostname"]', self.generator.get_first_name())
        self.fill_in_element('[name="ns1prefix"]', self.generator.get_first_name())
        self.fill_in_element('[name="ns2prefix"]', self.generator.get_first_name())
        self.fill_in_element('[name="rootpw"]', self.generator.get_password())
        self.driver.find_element_by_css_selector("input.bh_btn.bh_red").click()
        self.driver.implicitly_wait(1)
        self.driver.find_element_by_css_selector("a.bh_btn.bh_green").click()
        self.fill_in_element('[name="firstname"]', self.generator.get_first_name())
        self.fill_in_element('[name="lastname"]', self.generator.get_last_name())
        self.fill_in_element('[name="email"]', self.generator.get_email())
        self.fill_in_element('[name="password"]', self.generator.get_password())
        self.fill_in_element('[name="password2"]', self.generator.get_password())
        self.fill_in_element('[name="securityqans"]', self.generator.get_first_name())
        self.driver.find_element_by_xpath("//*[@value='bitpay']").click()
        self.driver.find_element_by_css_selector(".checkbox").click()
        # self.driver.find_element_by_css_selector("#finish_order").click()
        # self._close_browser()
