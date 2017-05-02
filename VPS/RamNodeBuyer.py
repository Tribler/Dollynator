from VPSBuyer import VPSBuyer



class RamNodeBuyer(VPSBuyer):
    def __init__(self):
        super(RamNodeBuyer, self).__init__()

    def register(self):
        self.spawn_browser()
        self.driver.get("https://ramnode.com/vps.php")
        self.driver.find_element_by_css_selector('#vzdiv > table:nth-of-type(1) > tbody > tr:nth-of-type(1) > td:nth-of-type(9) > a:nth-of-type(5)').click()
        self.fill_in_element('[name="hostname"]', self.generator.get_first_name())
        self.choose_select_element('tbody > tr:first-child > td.fieldarea > select', "Ubuntu 16.04 64-bit")
        self.driver.find_element_by_css_selector('input.checkout').click()
        self.driver.implicitly_wait(10)
        self.fill_in_element('[name="firstname"]', self.generator.get_first_name())
        self.fill_in_element('[name="lastname"]', self.generator.get_last_name())
        self.fill_in_element('[name="email"]', self.generator.get_email())
        self.fill_in_element('#newpw', self.generator.get_password())
        self.fill_in_element('tbody > tr:nth-of-type(6) > td:nth-of-type(2) > input', self.generator.get_password())
        self.fill_in_element('tbody > tr:first-child > td:nth-of-type(4) > input', self.generator.get_random_alphabetical_string(10))
        self.fill_in_element('[name="city"]', self.generator.get_city())
        self.fill_in_element('[name="postcode"]', self.generator.get_zipcode())
        self.choose_select_element('#country', "Netherlands")
        self.choose_select_element('#stateselect', "Limburg")
        self.fill_in_element('[name="phonenumber"]', self.generator.get_phone_num())
        self.fill_in_element('[name="securityqans"]', self.generator.get_random_alphabetical_string(10))
        self.choose_select_element('tbody > tr:nth-of-type(10) > td.fieldarea > select.form-control', "Google")
        self.driver.find_element_by_css_selector('div.signupfields.padded > label:nth-of-type(3) > input').click()
        self.driver.find_element_by_css_selector('#accepttos').click()
        self.driver.find_element_by_css_selector('input.ordernow.submitbutton').click()
        self.driver.implicitly_wait(10)
        self.driver.find_element_by_css_selector('tr > td:nth-of-type(2) > form:nth-of-type(2) > input:nth-of-type(11)').click()
        self.driver.implicitly_wait(10)
        self.driver.find_element_by_css_selector('#copy-tab > span').click()


        print(self.driver.find_element_by_css_selector('div.manual-box__amount__value.copy-cursor > span').text)
        print(self.driver.find_element_by_css_selector('div.manual-box__address__value.copy-cursor > div.manual-box__address__wrapper > div.manual-box__address__wrapper__value').text)
