import sys
from time import sleep

from splinter import Browser

browser = Browser('chrome')

def edit_title(recid):
    browser.visit('http://localhost:5000/editor/record/literature/{}'.format(recid))
    browser.find_by_id('email').type('admin@inspirehep.net')  # slowly=True
    browser.find_by_id('password').type('123456')
    browser.find_by_css('form > button').click()


    title = browser.find_by_xpath('//*[@id="/titles/0/title"]/table/tbody/tr/td[1]/div/string-input/div[2]')[0]
    title.click()
    title_input_xpath = '//*[@id="/titles/0/title"]/table/tbody/tr/td[1]/div/string-input/div[1]'
    if not browser.is_element_visible_by_xpath(title_input_xpath, 30):
        return 'title_input_xpath not visible!!!!'
        #print 'title_input_xpath not visible!!!!'
    title_input = browser.find_by_xpath(title_input_xpath)[0]
    title_input.type('a')

    save = browser.find_by_xpath('//*[@id="editor-toolbar"]/div/div/div[1]/div/button')[0]
    save.click()

    confirm_xpath = '/html/body/re-app/re-json-editor-wrapper/re-save-preview-modal/div/div/div/div[2]/div[2]/button[1]'
    if not browser.is_element_visible_by_xpath(confirm_xpath, 30):
        return 'title_input_xpath not visible!!!!'
        #print 'confirm_xpath not visible!!!!'
    sleep(2)
    confirm = browser.find_by_xpath(confirm_xpath)[0]
    confirm.click()

    return 'END'


recid = sys.argv[1]
if not recid:
    print('recid arg required')
    exit(1)

# 1498589  # 1 orcid.
# 1498185  # 100 orcids.
print(edit_title(recid))
browser.quit()
