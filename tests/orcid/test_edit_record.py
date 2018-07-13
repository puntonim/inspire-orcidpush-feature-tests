import time

from splinter import Browser

from services import flower, orcid
from tests import inspire_utils


ORCID = '0000-0002-0942-3697'
RECID = 1678462
TITLE_BASE = 'Some Results Arising from the Study of ORCID push at ts'


def test_edit_record_and_push_to_orcid():

    browser = Browser('chrome')

    inspire_utils.login_as_admin(browser)

    browser.visit('https://qa.inspirehep.net/editor/record/literature/{}'.format(RECID))
    title = browser.find_by_xpath('//*[@id="/titles/0/title"]/table/tbody/tr/td[1]/div/string-input/div[2]')[0]
    title.click()
    title_input_xpath = '//*[@id="/titles/0/title"]/table/tbody/tr/td[1]/div/string-input/div[1]'
    if not browser.is_element_visible_by_xpath(title_input_xpath, 30):
        print 'title_input_xpath not visible!'
        return
    title_input = browser.find_by_xpath(title_input_xpath)[0]
    new_title = '{} {}'.format(TITLE_BASE, time.time())
    title_input.value = new_title

    save = browser.find_by_xpath('//*[@id="editor-toolbar"]/div/div/div[1]/div/button')[0]
    save.click()

    confirm_xpath = '/html/body/re-app/re-json-editor-wrapper/re-save-preview-modal/div/div/div/div[2]/div[2]/button[1]'
    if not browser.is_element_visible_by_xpath(confirm_xpath, 30):
        print 'confirm_xpath not visible!'
        return
    time.sleep(2)
    confirm = browser.find_by_xpath(confirm_xpath)[0]
    confirm.click()

    browser.quit()

    if not flower.is_celery_task_orcid_push_successful(ORCID, RECID, 5*60):
        print('Celery task orcid_push for orcid={} and recid={} not found'.format(ORCID, RECID))

    if not orcid.is_title_in_orcid(new_title, ORCID, 5*60):
        print('Tile={} found'.format(new_title))




# TODO
# - test gest the env from command line and fetches the right test data