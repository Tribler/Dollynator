from VPSBuyer import VPSBuyer



class CCIHostingBuyer(VPSBuyer):
    def __init__(self):
        super(CCIHostingBuyer, self).__init__()

    def register(self):
        self.spawn_browser()
        self.driver.get("http://www.ccihosting.com/vps.php")
        self.driver.find_element_by_css_selector('#main > div:nth-of-type(3) > div:nth-of-type(1) > div:nth-of-type(3) > a.redbuttonfull').click()
        self.fill_in_element('#inputHostname', self.generator.get_first_name())
        self.fill_in_element('div.row > div:nth-of-type(1) > div:nth-of-type(5) > div:nth-of-type(2) > div:nth-of-type(1) > div.form-group > input.form-control', self.generator.get_first_name())
        self.fill_in_element('div.row > div:nth-of-type(1) > div:nth-of-type(5) > div:nth-of-type(2) > div:nth-of-type(2) > div.form-group > input.form-control', self.generator.get_first_name())
        self.fill_in_element('#inputRootpw', self.generator.get_password())
        self.choose_select_element('#productConfigurableOptions > div:nth-of-type(1) > div:nth-of-type(1) > div.form-group > select.form-control', 'Ubuntu 16.04')
        self.driver.implicitly_wait(10)
        self.driver.execute_script('document.getElementsByClassName("zopim")[1].style.display="none"')
        # self.driver.find_element_by_css_selector('.meshim_widget_widgets_IconFont.icon_font.close').click()
        # self.driver.implicitly_wait(10)
        self.driver.find_element_by_css_selector('#btnCompleteProductConfig').click()
        self.driver.execute_script('document.getElementsByClassName("zopim")[1].style.display="none"')
        self.driver.find_element_by_css_selector('#checkout').click()
        self.driver.execute_script('document.getElementsByClassName("zopim")[1].style.display="none"')
        self.fill_in_element('#inputFirstName', self.generator.get_first_name())
        self.fill_in_element('#inputLastName', self.generator.get_last_name())
        self.fill_in_element('#inputEmail', self.generator.get_email())
        self.fill_in_element('#inputPhone', self.generator.get_phone_num())
        self.fill_in_element('#containerNewUserSignup > div:nth-of-type(4) > div:nth-of-type(2) > div.form-group.prepend-icon > input.field', self.generator.get_random_alphabetical_string(10))
        self.fill_in_element('#inputCity', self.generator.get_city())
        self.fill_in_element('#inputPostcode', self.generator.get_zipcode())
        self.choose_select_element('#inputCountry', "Netherlands")
        self.choose_select_element('#stateselect', "Limburg")
        self.fill_in_element('#containerNewUserSecurity > div.row > div:nth-of-type(1) > div.form-group.prepend-icon > input.field', self.generator.get_password())
        self.fill_in_element('#containerNewUserSecurity > div.row > div:nth-of-type(2) > div.form-group.prepend-icon > input.field', self.generator.get_password())
        self.driver.find_element_by_css_selector('div.text-center > label:nth-of-type(2) > div.iradio_square-blue > ins.iCheck-helper').click()
        self.driver.find_element_by_css_selector('#iCheck-accepttos > ins.iCheck-helper').click()
        self.driver.find_element_by_css_selector('#btnCompleteOrder').click()
        print(self.driver.find_element_by_css_selector('#order_price').text)
        print(self.driver.find_element_by_css_selector('#order_uri').text)

        # self._fill_in_element('securityqans', self.generator.get_first_name())
        # self.driver.find_element_by_xpath("//*[@value='bitpay']").click()
        # self.driver.find_element_by_css_selector(".checkbox").click()
        # self.driver.find_element_by_css_selector("#finish_order").click()
        # self._close_browser()
