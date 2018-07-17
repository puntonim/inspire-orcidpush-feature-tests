"""
This code is meant to be run in a inspirehep shell (dev/qa/prod env).
It creates a record and an author to be used for the ORCID tests.

1. Run: setup_data()
2. Login in inspire using the ORCID profile 0000-0002-0942-3697 (rossonia92@gmail.com)
3. Run: allow_push()
"""

import copy
import os
import sys

from sqlalchemy import Integer, func

from invenio_db import db
from invenio_oauthclient.models import User, RemoteAccount
from invenio_pidstore.models import PersistentIdentifier
from invenio_records.models import RecordMetadata


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


def _insert_factories_in_sys_path():
    # Add the test factories dir in the system path.
    # Works on dev.
    sys.path.insert(0, os.path.join(os.getcwd(), 'tests', 'integration', 'helpers'))
    # Works on prod and qa..
    sys.path.insert(0, '/opt/inspire/src/inspire/tests/integration/helpers')


def _find_greatest_lit_pid():
    pid = db.session.query(func.max(PersistentIdentifier.pid_value.cast(Integer))).filter_by(pid_type='lit').scalar()
    pid = int(pid)
    return pid + 1


def _find_greatest_aut_pid():
    pid = db.session.query(func.max(PersistentIdentifier.pid_value.cast(Integer))).filter_by(pid_type='aut').scalar()
    pid = int(pid)
    return pid + 1


def _create_record(record_json, **kwargs):
    from factories.db.invenio_records import TestRecordMetadata
    factory = TestRecordMetadata.create_from_kwargs(json=record_json, **kwargs)
    return factory


def _get_record_metadata(type_, recid):
    pid = PersistentIdentifier.get(type_, recid)
    return RecordMetadata.query.get(pid.object_uuid)


def _setup_record(author_recid):
    pid = _find_greatest_lit_pid()
    record_json['control_number'] = pid
    record_json['authors'][0]['recid'] = author_recid
    record_json['authors'][0]['record']['$ref'] = "{}/api/authors/{}".format(BASE_URL, author_recid)

    factory = _create_record(record_json)
    db.session.commit()
    return factory.record_metadata


def _setup_author():
    pid = _find_greatest_aut_pid()
    author_json['control_number'] = pid

    factory = _create_record(author_json, pid_type='aut')
    db.session.commit()
    return factory.record_metadata

# def _edit_record_metadata_json(type_, recid, json_data, author_recid=None):
#     """
#     Eg: _edit_record_metadata_json('lit', 1682387, record_json, 1682180)
#     """
#     record = _get_record_metadata(type_, recid)
#
#     if author_recid:
#         json_data['authors'][0]['recid'] = author_recid
#         json_data['authors'][0]['record']['$ref'] = "{}/api/authors/{}".format(BASE_URL, author_recid)
#
#     record.json = json_data
#     db.session.add(record)
#     db.session.commit()


def setup_data():
    _insert_factories_in_sys_path()

    # Author.
    author = _setup_author()
    print('Author created with control number: ', author.json['control_number'])

    # Record.
    record = _setup_record(author_recid=author.json['control_number'])
    print('Record created with control number: ', record.json['control_number'])


def allow_push():
    user = User.query.filter_by(email='rossonia92@gmail.com').one()
    remote_account = user.remote_accounts[0]
    extra_data = copy.copy(remote_account.extra_data)
    extra_data['allow_push'] = True
    remote_account.extra_data = extra_data
    print('Token set to allow push: {}'.format(remote_account.remote_tokens[0].access_token))
    db.session.commit()
