import time

import config

from .client import OrcidClient


def _get_oauth_token(orcid):
    # Ugly way to get the token because the key in the config file is the orcid.
    if config.ENV == 'dev':
        return config.get('orcid-api-tokens-dev', orcid)
    elif config.ENV == 'qa':
        return config.get('orcid-api-tokens-qa', orcid)
    elif config.ENV == 'prod':
        return config.get('orcid-api-tokens-prod', orcid)


class OrcidSearcher(object):
    def __init__(self, orcid):
        oauth_token = _get_oauth_token(orcid)
        self.orcid = OrcidClient(oauth_token, orcid)

    def search_by_title(self, title):
        summaries = self.orcid.get_all_works_summary()

        for work in summaries['group']:
            for summary in work['work-summary']:
                if title == summary['title']['title']['value']:
                    return True
        return False


def is_title_in_orcid(title, orcid, timeout):
    end_time = time.time() + timeout

    searcher = OrcidSearcher(orcid)

    while time.time() < end_time:
        if searcher.search_by_title(title):
            print('Title={} found at orcid.org for orcid={}'.format(title, orcid))
            return True
        print('Title={} not found at orcid.org for orcid={}'.format(title, orcid))
        time.sleep(2)

    return False
