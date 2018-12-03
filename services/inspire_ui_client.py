import config
from test_utils import test_data


test_data.set(
    LOGIN_ENDPOINT='user/login',
    USERNAME_QA=config.get('inspire-admin-user-qa', 'username'),
    USERNAME_DEV='admin@inspirehep.net',
    USERNAME_PROD=config.get('inspire-admin-user-prod', 'username'),

    PASSWORD_QA=config.get('inspire-admin-user-qa', 'password'),
    PASSWORD_DEV='password',
    PASSWORD_PROD=config.get('inspire-admin-user-prod', 'password'),
)


def login_as_admin(browser):
    browser.visit('{}/{}'.format(test_data.BASEURL, test_data.LOGIN_ENDPOINT))
    browser.find_by_css('button.login-button').click()
    browser.focus_on_new_tab(2)
    browser.find_visible_by_css('#userId', wait_time=30).type(test_data.USERNAME)
    browser.find_by_css('#password').type(test_data.PASSWORD)
    browser.find_by_css('#form-sign-in-button').click()
    browser.focus_on_new_tab(1, wait_time=180)
