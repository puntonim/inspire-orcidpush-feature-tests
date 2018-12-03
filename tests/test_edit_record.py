import config
from test_utils import test_data
from services import inspire_ui_client, orcid_api_client, flower_api_client
from test_utils.browser import Chrome


ORCID = '0000-0002-5073-0816'

test_data.set(
    # For all envs.
    ORCID=ORCID,
    TOKEN_QA=config.get('orcid-api-tokens-qa', ORCID),
    TOKEN_PROD=config.get('orcid-api-tokens-prod', ORCID),
    TOKEN_DEV=config.get('orcid-api-tokens-dev', ORCID),
    RECORD_EDITOR_ENDPOINT='workflows/edit_article',
    USER_PROFILE_ENDPOINT='user/profile',
    SAVE_XPATH='//*[@id="editor-toolbar"]/div/div/div[1]/re-holdingpen-save-button/button',
    RECID_DEV=20,
    RECID_QA=20,
    RECID_PROD=20,
)


def test_orcid_login():
    browser = Chrome()
    inspire_ui_client.login_as_admin(browser)
    browser.visit('{}/{}'.format(test_data.BASEURL, test_data.USER_PROFILE_ENDPOINT))
    # TODO This assertion has to be improved but at the moment the profile page
    # is under construction (and is empty).
    assert browser.is_element_not_visible_by_css('#userId', wait_time=2)
    browser.quit()


import pytest
@pytest.mark.skip
def test_edit_record_and_push_to_orcid():
    # Clean up the orcid work.
    orcid_api_client.delete_work(test_data.ORCID, test_data.TOKEN, test_data.RECID)
    assert not orcid_api_client.get_putcode_for_work(test_data.ORCID, test_data.TOKEN, test_data.RECID)

    browser = Chrome()
    inspire_ui_client.login_as_admin(browser)
    browser.visit('{}/{}/{}'.format(test_data.BASEURL, test_data.RECORD_EDITOR_ENDPOINT, test_data.RECID))
    save = browser.find_visible_by_xpath(test_data.SAVE_XPATH)[0]
    save.click()

    # Ensure (using Flower) the Celery task has been successfully executed.
    assert flower_api_client.is_orcid_push_task_successful(test_data.ORCID, test_data.RECID, 60*5)

    # Ensure the work is visible in orcid.
    assert orcid_api_client.get_putcode_for_work(test_data.ORCID, test_data.TOKEN, test_data.RECID)
    browser.quit()