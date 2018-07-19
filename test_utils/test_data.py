"""
Setup test data for a specific test module.

This module has some magic that makes it behave like an instance object.
Example:
    from tests import inspire_utils, test_data
    test_data.set(
        # For all envs.
        ORCID='0000-0002-0942-3697',

        # Environment specific.
        RECID_QA=1678462,
    )

    def test_edit_record_and_push_to_orcid():
        ...
        browser.visit('{}/{}/{}'.format(test_data.BASEURL, test_data.ORCID, test_data.RECID))
"""
import sys

import config


DEFAULTS = dict(
    BASEURL_QA='https://qa.inspirehep.net',
    BASEURL_PROD='https://labs.inspirehep.net',
    BASEURL_DEV='http://127.0.0.1:xxx',
)


class _TestData(object):
    def __init__(self, original_module):
        self.original_module = original_module
        self.data = DEFAULTS

    def __getattr__(self, name):
        """
        Override in order to let the . access, like:
        obj.BASEURL
        """
        # First try to access the original attribute.
        try:
            return getattr(self.original_module, name)
        except AttributeError:
            pass

        # If the original attribute failed, then check in self.data.
        # If name is ORCID it will first search for ORCID_QA (or *_DEV or *_PROD
        # depending on the active environment) then for ORCID in self.data.
        env = config.ENV.upper() if config.ENV else ''
        name_w_env = '{}_{}'.format(name, env)
        if name_w_env in self.data:
            return self.data[name_w_env]
        elif name in self.data:
            return self.data[name]
        else:
            raise AttributeError('No {} nor {} attribute'.format(name_w_env, name))

    def set(self, **kwargs):
        self.data.update(kwargs)


# Note: this is a trick to make this module behave like an instance
# of the class _TestData.
# https://stackoverflow.com/a/7668273/1969672
sys.modules[__name__] = _TestData(sys.modules[__name__])
