import time
from splinter.driver.webdriver.chrome import WebDriver as ChromeWebDriver


class Chrome(ChromeWebDriver):
    def find_visible_by_xpath(self, xpath, *args, **kwargs):
        wait_time = kwargs.pop('wait_time', None)
        if not self.is_element_visible_by_xpath(xpath, wait_time=wait_time):
            assert False, '{} not visible'.format(xpath)

        element = self.find_by_xpath(xpath, *args, **kwargs)

        # Wait for the element to load properly for 15 secs.
        end_time = time.time() + 15
        while not element and time.time() < end_time:
            element = self.find_by_xpath(xpath, *args, **kwargs)

        if element:
            return element
        else:
            assert False, '{} not found'.format(xpath)
