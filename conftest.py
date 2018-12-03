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


@pytest.fixture(scope='session', autouse=True)
def env(request):
    env = request.config.getoption('--env').lower()
    if env not in ('dev', 'qa', 'prod'):
        raise ValueError('--env possible values are: dev|qa|prod')
    config.ENV = env

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
