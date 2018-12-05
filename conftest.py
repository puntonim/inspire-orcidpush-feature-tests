import pytest

import config
import inspire_service_orcid.conf
import service_flower.conf
from test_utils import test_data


test_data.set(
    # For all envs.
    FLOWER_API_URL_QA='https://inspire-qa-worker3-task1.cern.ch/api',
    FLOWER_API_URL_PROD='https://inspire-prod-worker3-task1.cern.ch/api',
    FLOWER_API_URL_DEV='http://localhost:5555/api',
    FLOWER_API_HTTPAUTH_USERNAME_QA=config.get('flower-api-httpauth-qa', 'username'),
    FLOWER_API_HTTPAUTH_PASSWORD_QA=config.get('flower-api-httpauth-qa', 'password'),
    FLOWER_API_HTTPAUTH_USERNAME_PROD=config.get('flower-api-httpauth-prod', 'username'),
    FLOWER_API_HTTPAUTH_PASSWORD_PROD=config.get('flower-api-httpauth-prod', 'password'),
)


def pytest_addoption(parser):
    parser.addoption('--env', action='store', default='', help='Environment: dev|qa|prod')
    parser.addoption('--remote', action='store', default=False, help='Use SauceLabs remote webdriver: true|false')
    parser.addoption('--headless', action='store', default=False, help='Use headless Chrome (not available in remote): true|false')


@pytest.fixture(scope='session', autouse=True)
def env(request):
    # Parse option: env.
    env = request.config.getoption('--env').lower()
    if env not in ('dev', 'qa', 'prod'):
        raise ValueError('--env possible values are: dev|qa|prod')
    config.ENV = env

    # Parse option: remote.
    is_remote = request.config.getoption('--remote')
    is_remote = is_remote or ''
    if is_remote.lower() in ('true', 'yes'):
        is_remote = True
    else:
        is_remote = False
    config.IS_REMOTE = is_remote

    # Parse option: headless.
    is_headless = request.config.getoption('--headless')
    is_headless = is_headless or ''
    if is_headless.lower() in ('true', 'yes'):
        is_headless = True
    else:
        is_headless = False
    config.IS_HEADLESS = is_headless

    d = dict(
        # DO_USE_SANDBOX=False,
        CONSUMER_KEY=config.get('orcid-api', 'consumer_key'),  # Inspire official ORCID account.
        CONSUMER_SECRET=config.get('orcid-api', 'consumer_secret'),
        DO_ENABLE_METRICS=False,
    )
    inspire_service_orcid.conf.settings.configure(**d)

    d = dict(
        BASE_URL=test_data.FLOWER_API_URL,
        REQUEST_TIMEOUT=30,
        HTTP_AUTH_USERNAME=test_data.FLOWER_API_HTTPAUTH_USERNAME,
        HTTP_AUTH_PASSWORD=test_data.FLOWER_API_HTTPAUTH_PASSWORD,
    )
    service_flower.conf.settings.configure(**d)
