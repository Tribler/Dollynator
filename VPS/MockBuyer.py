from VPSBuyer import VPSBuyer


class MockBuyer(VPSBuyer):
    def __init__(self):
        super(MockBuyer, self).__init__()

    def buy(self):
        self.spawn_browser()
        self.driver.get("https://duckduckgo.com")
        self.close_browser()
