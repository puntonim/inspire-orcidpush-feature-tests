import config

from tests import test_data


test_data.set(
    LOGIN_ENDPOINT='login/?local=1',
    USERNAME_QA=config.get('inspire-admin-user-qa', 'username'),
    USERNAME_DEV='admin@inspirehep.net',
    USERNAME_PROD=config.get('inspire-admin-user-prod', 'username'),

    PASSWORD_QA=config.get('inspire-admin-user-qa', 'password'),
    PASSWORD_DEV='password',
    PASSWORD_PROD=config.get('inspire-admin-user-prod', 'password'),
)


def login_as_admin(browser):
    browser.visit('{}/{}'.format(test_data.BASEURL, test_data.LOGIN_ENDPOINT))

    browser.find_by_id('email').type(test_data.USERNAME)
    browser.find_by_id('password').type(test_data.PASSWORD)
    browser.find_by_css('form > button').click()
