from orcid import MemberAPI

import config

from .models import GetAllWorksSummaryResponse


class OrcidClient(object):
    def __init__(self, oauth_token, orcid):
        self.oauth_token = oauth_token
        self.orcid = orcid
        client_key = config.get('orcid-api', 'consumer_key')
        client_secret = config.get('orcid-api', 'consumer_secret')
        sandbox = False
        self.memberapi = MemberAPI(client_key, client_secret, sandbox, timeout=30)

    def get_all_works_summary(self):
        response = self.memberapi.read_record_member(
            self.orcid,
            'works',
            self.oauth_token,
            accept_type='application/orcid+json',
        )
        """
        Response is a dict like:
        {'group': [{'external-ids': {'external-id': [{'external-id-relationship': 'SELF',
                                                      'external-id-type': 'doi',
                                                      'external-id-url': {'value': 'http://dx.doi.org/10.1016/0029-5582(61)90469-2'},
                                                      'external-id-value': '10.1016/0029-5582(61)90469-2'}]},
                    'last-modified-date': {'value': 1519143190177},
                    'work-summary': [{'created-date': {'value': 1516716146242},
                                      'display-index': '0',
                                      'external-ids': {'external-id': [{'external-id-relationship': 'SELF',
                                                                        'external-id-type': 'doi',
                                                                        'external-id-url': {'value': 'http://dx.doi.org/10.1016/0029-5582(61)90469-2'},
                                                                        'external-id-value': '10.1016/0029-5582(61)90469-2'}]},
                                      'last-modified-date': {'value': 1519143190177},
                                      'path': '/0000-0002-1825-0097/work/912978',
                                      'publication-date': {'day': None,
                                                           'media-type': None,
                                                           'month': None,
                                                           'year': {'value': '1961'}},
                                      'put-code': 912978,
                                      'source': {'source-client-id': {'host': 'sandbox.orcid.org',
                                                                      'path': 'CHANGE_ME',
                                                                      'uri': 'http://sandbox.orcid.org/client/CHANGE_ME'},
                                                 'source-name': {'value': 'INSPIRE-PROFILE-PUSH'},
                                                 'source-orcid': None},
                                      'title': {'subtitle': None,
                                                'title': {'value': 'Partial Symmetries of Weak Interactions'},
                                                'translated-title': None},
                                      'type': 'JOURNAL_ARTICLE',
                                      'visibility': 'PUBLIC'}]}],
         'last-modified-date': {'value': 1519143233490},
         'path': '/0000-0002-1825-0097/works'}
        """
        return GetAllWorksSummaryResponse(response)
