import pytest

import config


def pytest_addoption(parser):
    parser.addoption('--env', action='store', default='', help='Environment: dev|qa|prod')


@pytest.fixture(scope='session', autouse=True)
def env(request):
    env = request.config.getoption('--env').lower()
    if env not in ('dev', 'qa', 'prod'):
        raise ValueError('--env possible values are: dev|qa|prod')
    config.ENV = env
