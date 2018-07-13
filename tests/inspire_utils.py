import config


def login_as_admin(browser):
    browser.visit('https://qa.inspirehep.net/login/?local=1')

    ##### DEV
    ##### username = 'admin@inspirehep.net'
    ##### password = 'password'

    username = config.get('inspire-admin-user-qa', 'username')
    password = config.get('inspire-admin-user-qa', 'password')

    browser.find_by_id('email').type(username)
    browser.find_by_id('password').type(password)
    browser.find_by_css('form > button').click()
