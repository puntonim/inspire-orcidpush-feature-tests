import time
from splinter.driver.webdriver.chrome import WebDriver as ChromeWebDriver


class Chrome(ChromeWebDriver):
    def find_visible_by_xpath(self, xpath, *args, **kwargs):
        wait_time = kwargs.pop('wait_time', None)
        if not self.is_element_visible_by_xpath(xpath, wait_time=wait_time):
            assert False, '{} not visible'.format(xpath)

        element = self.find_by_xpath(xpath, *args, **kwargs)

        # Wait for the element to load properly for up to 15 secs.
        start_time = time.time()
        while not element and time.time() < start_time + 15:
            element = self.find_by_xpath(xpath, *args, **kwargs)

        if element:
            return element
        else:
            assert False, '{} not found'.format(xpath)

    def find_visible_by_css(self, css, *args, **kwargs):
        wait_time = kwargs.pop('wait_time', None)
        if not self.is_element_visible_by_css(css, wait_time=wait_time):
            assert False, '{} not visible'.format(css)

        element = self.find_by_css(css, *args, **kwargs)

        # Wait for the element to load properly for up to 15 secs.
        start_time = time.time()
        while not element and time.time() < start_time + 15:
            element = self.find_by_css(css, *args, **kwargs)

        if element:
            return element
        else:
            assert False, '{} not found'.format(css)

    def focus_on_new_tab(self, expected_num_tabs, wait_time=30):
        start_time = time.time()
        while time.time() < start_time + wait_time:
            time.sleep(1)
            if len(self.windows) == expected_num_tabs:
                self.windows.current = self.windows[-1]
                self.find_visible_by_css('html', wait_time=wait_time)
                return
        assert False, 'the browser doe not have {} tabs'.format(expected_num_tabs)
