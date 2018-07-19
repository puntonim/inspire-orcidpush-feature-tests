from splinter.driver.webdriver.chrome import WebDriver as ChromeWebDriver


class Chrome(ChromeWebDriver):
    def find_visible_by_xpath(self, xpath, *args, **kwargs):
        wait_time = kwargs.pop('wait_time', None)
        if not self.is_element_visible_by_xpath(xpath, wait_time=wait_time):
            assert False, '{} not visible'.format(xpath)

        return self.find_by_xpath(xpath, *args, **kwargs)
