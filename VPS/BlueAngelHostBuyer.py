from VPSBuyer import VPSBuyer



class BlueAngelHostBuyer(VPSBuyer):
    def __init__(self):
        super(BlueAngelHostBuyer, self).__init__()

    def buy(self):
        self._spawn_browser()
        self.driver.get("https://www.blueangelhost.com/kvm-vps/")
        self.driver.find_element_by_css_selector('#annual_price > div:nth-of-type(1) > div.plan_table > a.btn').click()
        self._fill_in_element('#inputHostname', self.generator.get_first_name())
        self._fill_in_element('#inputRootpw', self.generator.get_password())
        self._fill_in_element('div.row > div:nth-of-type(1) > div:nth-of-type(5) > div:nth-of-type(2) > div:nth-of-type(1) > div.form-group > input.form-control', self.generator.get_first_name())
        self._fill_in_element('div.row > div:nth-of-type(1) > div:nth-of-type(5) > div:nth-of-type(2) > div:nth-of-type(2) > div.form-group > input.form-control', self.generator.get_first_name())
        self._choose_select_element('#productConfigurableOptions > div:nth-of-type(1) > div:nth-of-type(1) > div.form-group > select.form-control', "Ubuntu")
        self._choose_select_element('#productConfigurableOptions > div:nth-of-type(1) > div:nth-of-type(2) > div.form-group > select.form-control', "64 Bit")
        self.driver.implicitly_wait(10)
        self.driver.find_element_by_css_selector('#btnCompleteProductConfig').click()
        self.driver.implicitly_wait(10)
        self.driver.find_element_by_css_selector('#checkout').click()
        self._fill_in_element('#inputFirstName', self.generator.get_first_name())
        self._fill_in_element('#inputLastName', self.generator.get_last_name())
        self._fill_in_element('#inputEmail',self.generator.get_email())
        self._fill_in_element('#inputPhone', self.generator.get_phone_num())
        self._fill_in_element('#containerNewUserSignup > div:nth-of-type(4) > div:nth-of-type(2) > div.form-group.prepend-icon > input.field', self.generator.get_random_alphabetical_string(10))
        self._fill_in_element('#inputCity', self.generator.get_city())
        self._fill_in_element('#inputPostcode', self.generator.get_zipcode())
        self._choose_select_element('#inputCountry', "Netherlands")
        self._choose_select_element('#stateselect', "Limburg")
        self._choose_select_element('div.form-group > select.form-control', "Google")
        self._fill_in_element('#containerNewUserSecurity > div.row > div:nth-of-type(1) > div.form-group.prepend-icon > input.field', self.generator.get_password())
        self._fill_in_element('#containerNewUserSecurity > div.row > div:nth-of-type(2) > div.form-group.prepend-icon > input.field', self.generator.get_password())
        self.driver.find_element_by_css_selector('div.text-center > label:nth-of-type(3) > div.iradio_square-blue > ins.iCheck-helper').click()
        self.driver.find_element_by_css_selector('#iCheck-accepttos > ins.iCheck-helper').click()
        self.driver.find_element_by_css_selector('#btnCompleteOrder').click()
        self.driver.find_element_by_css_selector('form > input:nth-of-type(11)').click()
        self.driver.find_element_by_css_selector('#copy-tab > span').click()
        print(self.driver.find_element_by_css_selector('div.manual-box__amount__value.copy-cursor > span').text)
        print(self.driver.find_element_by_css_selector('div.manual-box__address__value.copy-cursor > div.manual-box__address__wrapper > div.manual-box__address__wrapper__value').text)


