import time

from splinter import Browser

from services import flower, orcid
from tests import inspire_utils, test_data


test_data.set(
    # For all envs.
    ORCID='0000-0002-0942-3697',
    RECORD_EDITOR_ENDPOINT='editor/record/literature',
    TITLE_XPATH='//*[@id="/titles/0/title"]/table/tbody/tr/td[1]/div/string-input/div[2]',
    TITLE_INPUT_XPATH='//*[@id="/titles/0/title"]/table/tbody/tr/td[1]/div/string-input/div[1]',
    SAVE_XPATH='//*[@id="editor-toolbar"]/div/div/div[1]/div/button',
    CONFIRM_XPATH='/html/body/re-app/re-json-editor-wrapper/re-save-preview-modal/div/div/div/div[2]/div[2]/button[1]',

    # Environment specific.
    TITLE_BASE_QA='Some Results Arising from the Study of ORCID push in QA at ts',
    TITLE_BASE_PROD='Some Results Arising from the Study of ORCID push in PROD at ts',
    TITLE_BASE_DEV='Some Results Arising from the Study of ORCID push in DEV at ts',

    RECID_DEV=1498590,  # author: 1401175  # TODO: the token is missing in my env
    RECID_QA=1678462,  # author: 1669909
    RECID_PROD=1682606,  # author: 1682180  # TODO: the record gets deleted
)


def test_edit_record_and_push_to_orcid():
    browser = Browser('chrome')

    inspire_utils.login_as_admin(browser)

    browser.visit('{}/{}/{}'.format(test_data.BASEURL, test_data.RECORD_EDITOR_ENDPOINT, test_data.RECID))

    title = browser.find_by_xpath(test_data.TITLE_XPATH)[0]
    title.click()
    if not browser.is_element_visible_by_xpath(test_data.TITLE_INPUT_XPATH, 30):
        print('title_input_xpath not visible!')
        return

    title_input = browser.find_by_xpath(test_data.TITLE_INPUT_XPATH)[0]
    # Ensure we are about to edit the right record.
    assert test_data.TITLE_BASE_DEV[:35] in title_input.value
    new_title = '{} {}'.format(test_data.TITLE_BASE, time.time())
    title_input.value = new_title

    save = browser.find_by_xpath(test_data.SAVE_XPATH)[0]
    save.click()

    if not browser.is_element_visible_by_xpath(test_data.CONFIRM_XPATH, 30):
        print 'confirm_xpath not visible!'
        return
    time.sleep(2)
    confirm = browser.find_by_xpath(test_data.CONFIRM_XPATH)[0]
    confirm.click()

    browser.quit()

    if not flower.is_celery_task_orcid_push_successful(test_data.ORCID, test_data.RECID, 5*60):
        print('Celery task orcid_push for orcid={} and recid={} not found'.format(test_data.ORCID, test_data.RECID))

    if not orcid.is_title_in_orcid(new_title, test_data.ORCID, 5*60):
        print('Title={} not found'.format(new_title))
