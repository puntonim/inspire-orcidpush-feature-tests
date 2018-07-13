import time

from .client import OrcidClient

import config


class OrcidSearcher(object):
    def __init__(self, orcid):
        oauth_token = config.get('orcid-api-tokens', orcid)
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
            print('Tile={} found at orcid.org for orcid={}'.format(title, orcid))
            return True
        print('Tile={} not found at orcid.org for orcid={}'.format(title, orcid))
        time.sleep(2)

    return False
