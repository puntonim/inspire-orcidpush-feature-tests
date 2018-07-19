"""
This code is meant to be run in a inspirehep shell (dev/qa/prod env).
It creates a record and an author to be used for the ORCID tests.

1. Run: setup_data('qa')
2. Login in inspire using the ORCID profile 0000-0002-0942-3697 (rossonia92@gmail.com)
3. Run: allow_push()
"""

import copy

from invenio_db import db
from invenio_oauthclient.models import User, RemoteAccount

from inspirehep.modules.records.api import InspireRecord


BASE_URL_DEV = 'http://127.0.0.1:5000'
BASE_URL_QA = 'https://qa.inspirehep.net'
BASE_URL_PROD = 'https://labs.inspirehep.net'

# SET THIS ACCORDINGLY.
BASE_URL = BASE_URL_PROD


record_json = {
    "$schema": "{}/schemas/records/hep.json".format(BASE_URL),
    "_collections": [
      "Literature"
    ],
    "titles": [
        {
            "source":"submitter",
            "title":"Some Results Arising from the Study of ORCID push",
        }
    ],
    "abstracts": [
        {
            "source": "submitter",
            "value": "This is a record used for testing the ORCID feature."
        }
    ],
    "acquisition_source": {
        "datetime":"2018-07-05T09:25:52.915736",
        "email":"annette.holtkamp@cern.ch",
        "internal_uid":50004,
        "method":"submitter",
        "orcid":"0000-0002-4133-3528",
        "source":"submitter",
        #"submission_number":"115236"
    },
    "authors":[
        {
            "full_name":"Rossoni, A.",
            "inspire_roles":[
                "author"
            ],
            "curated_relation": True,
            #"recid":1259096,  # micha,
            "record": {
                #"$ref": "http://qa.inspirehep.net/api/authors/1259096"
            },
        }
    ],
    "dois": [
        {
            "source": "submitter",
            "value": "10.1000/test.orcid.push",
        },
    ],
    "collaborations": [
    ],
    "document_type": [
      "article"
    ],
    "preprint_date": "2017-05",
    #"control_number":0000,
}


author_json = {
    '$schema': '{}/schemas/records/authors.json'.format(BASE_URL),
    '_collections': ['Authors'],
    'document_type': [],
    'acquisition_source': {
        'datetime': '2018-04-06T07:46:23.134659',
        'email': 'rossonia92@gmail.com',
        'method': 'submitter',
        'orcid': '0000-0002-0942-3697',
        #'submission_number': u'975231'
    },
    'arxiv_categories': ['hep-th'],
    #'control_number': 1259096,
    'deleted': False,
    'ids': [{'schema': 'ORCID', 'value': '0000-0002-0942-3697'}],
    'legacy_creation_date': u'2013-10-16',
    'name': {'preferred_name': 'Rossoni Andrea', 'value': 'Rossoni Andrea'},
    'status': 'active',
    'stub': False,
}


# from invenio_files_rest.models import Bucket, ObjectVersion
# from invenio_pidstore.models import PersistentIdentifier
# from invenio_records_files.models import RecordsBuckets
# from invenio_records.models import RecordMetadata
# from redis import StrictRedis
# from flask import current_app
#
# def _delete_record(record):
#     try:
#         rec_bucket = RecordsBuckets.query.filter(RecordsBuckets.record == record).one()
#         bucket = rec_bucket.bucket
#         ObjectVersion.query.filter(ObjectVersion.bucket == bucket).delete()
#         db.session.delete(bucket)
#         db.session.delete(rec_bucket)
#     except Exception:
#         pass
#     PersistentIdentifier.query.filter(PersistentIdentifier.object_uuid == record.id).delete()
#     db.session.delete(record)
#     db.session.commit()
#
# def _get_record_metadata(type_, recid):
#     pid = PersistentIdentifier.get(type_, recid)
#     return RecordMetadata.query.get(pid.object_uuid)

from redis import StrictRedis
from flask import current_app

def delete_cached_putcodes(orcid, recid):
    redis_url = current_app.config.get('CACHE_REDIS_URL')
    r = StrictRedis.from_url(redis_url)
    r.delete('orcidcache:{}:{}'.format(orcid, recid))

def _setup_author():
    author = InspireRecord.create(author_json)
    author.commit()
    db.session.commit()
    return author


def _setup_record(author_recid):
    # Update author's recid in record.
    record_json['authors'][0]['record']['$ref'] = "{}/api/authors/{}".format(BASE_URL, author_recid)

    record = InspireRecord.create(record_json)
    record.commit()
    db.session.commit()
    return record


def setup_data(env):
    if env == 'dev':
        env = '127.0.0.1'
    if env not in BASE_URL:
        print('You probably forgot to change the global var BASE_URL')

    # Author.
    author = _setup_author()
    print('Author created with control number: ', author['control_number'])

    # Record.
    record = _setup_record(author_recid=author['control_number'])
    print('Record created with control number: ', record['control_number'])


def allow_push():
    user = User.query.filter_by(email='rossonia92@gmail.com').one()
    remote_account = user.remote_accounts[0]
    extra_data = copy.copy(remote_account.extra_data)
    extra_data['allow_push'] = True
    remote_account.extra_data = extra_data
    print('Token set to allow push: {}'.format(remote_account.remote_tokens[0].access_token))
    db.session.commit()
