from VPSBuyer import VPSBuyer


class BlackhostBuyer(VPSBuyer):
    def __init__(self):
        super(BlackhostBuyer, self).__init__()

    def buy(self):
        self._spawn_browser()
        self.driver.get("https://black.host/unmetered-vps-hosting")
        self.driver.find_element_by_css_selector(".servers ul.red li .info .noline a").click()
        self._fill_in_element('hostname', self.generator.get_first_name())
        self._fill_in_element('ns1prefix', self.generator.get_first_name())
        self._fill_in_element('ns2prefix', self.generator.get_first_name())
        self._fill_in_element('rootpw', self.generator.get_password())
        self.driver.find_element_by_css_selector(".bh_btn.bh_red").click()
        self.driver.find_element_by_css_selector(".bh_btn.bh_green").click()
        self._fill_in_element('firstname', self.generator.get_first_name())
        self._fill_in_element('lastname', self.generator.get_last_name())
        self._fill_in_element('email', self.generator.get_email())
        self._fill_in_element('password', self.generator.get_password())
        self._fill_in_element('password2', self.generator.get_password())
        self._fill_in_element('securityqans', self.generator.get_first_name())
        self.driver.find_element_by_xpath("//*[@value='bitpay']").click()
        self.driver.find_element_by_css_selector(".checkbox").click()
        self.driver.find_element_by_css_selector("#finish_order").click()
        # self._close_browser()
