"""
This code is meant to be run in a inspirehep shell (dev/qa/prod env).
It creates a record and an author to be used for the ORCID tests.

1. Run: setup_data('qa')
2. Login in inspire using the ORCID profile 0000-0002-0942-3697 (rossonia92@gmail.com)
3. Run: allow_push()
"""
import random
import sys

from flask import current_app
from redis import StrictRedis
from sqlalchemy import cast, type_coerce
from sqlalchemy.dialects.postgresql import JSONB

from invenio_db import db
from invenio_files_rest.models import Bucket, ObjectVersion
from invenio_oauthclient.models import RemoteToken, User, RemoteAccount, UserIdentity
from invenio_pidstore.models import PersistentIdentifier, RecordIdentifier
from invenio_records.models import RecordMetadata
from invenio_records_files.models import RecordsBuckets

from inspirehep.modules.orcid.utils import get_literature_recids_for_orcid
from inspirehep.modules.records.api import InspireRecord



ENVS_BASEURLS = {
    'local': 'http://127.0.0.1:5000',
    'qa': 'https://qa.inspirehep.net',
    'prod': 'https://labs.inspirehep.net',
}


# SET THIS ACCORDINGLY.
BASE_URL = None


# Test data.
ORCID = '0000-0002-0942-3697'
EMAIL = 'rossonia92@gmail.com'
FULL_NAME = 'Rossoni Andrea'
SHORT_NAME = 'Rossoni, A.'


_USED_NUMS = []

def random_number():
    global _USED_NUMS
    num = random.randint(1, 1000)
    while num not in _USED_NUMS:
        num = random.randint(1, 1000)
        _USED_NUMS.append(num)
    return num


def get_record_json():
    record_json = {
        "$schema": "{}/schemas/records/hep.json".format(BASE_URL),
        "_collections": [
          "Literature"
        ],
        "titles": [
            {
                "source":"submitter",
                "title":"Some Results Arising from the Study of ORCID push in {}",
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
                "full_name":SHORT_NAME,
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
                "value": "10.1000/test.orcid.push.{}".format(BASE_URL),
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
    return record_json


def get_author_json():
    author_json = {
        '$schema': '{}/schemas/records/authors.json'.format(BASE_URL),
        '_collections': ['Authors'],
        'document_type': [],
        'acquisition_source': {
            'datetime': '2018-04-06T07:46:23.134659',
            'email': EMAIL,
            'method': 'submitter',
            'orcid': ORCID,  # IS IT REQUIRED???????
            #'submission_number': u'975231'
        },
        'arxiv_categories': ['hep-th'],
        #'control_number': 1259096,
        'deleted': False,
        'ids': [{'schema': 'ORCID', 'value': ORCID}],
        'legacy_creation_date': '2013-10-16',
        'name': {'preferred_name': FULL_NAME, 'value': FULL_NAME},
        'status': 'active',
        'stub': False,
    }
    return author_json



###############################################################################
## DELETE STUFF
def _delete_record(record):
    rec_bucket = RecordsBuckets.query.filter(RecordsBuckets.record == record).one_or_none()
    if rec_bucket:
        bucket = rec_bucket.bucket
        ObjectVersion.query.filter(ObjectVersion.bucket == bucket).delete()
        db.session.delete(bucket)
        db.session.delete(rec_bucket)
    pid = PersistentIdentifier.query.filter(PersistentIdentifier.object_uuid == record.id).one()
    recid = RecordIdentifier.query.get(pid.pid_value)
    db.session.delete(recid)
    db.session.delete(pid)
    db.session.delete(record)
    db.session.commit()

def delete_record_by_pid():
    pid_type = raw_input('Which pid_type (lit|aut)? ')
    if pid_type not in ('lit', 'aut'):
        print('Type unknown: {}'.format(pid_type))
        sys.exit(1)
    pid_value = raw_input('Which pid_value or recid or control_number? ')
    record = RecordMetadata.query.filter(RecordMetadata.id == PersistentIdentifier.object_uuid)\
        .filter(PersistentIdentifier.pid_value == str(pid_value),
                PersistentIdentifier.pid_type == pid_type).one()

    _delete_record(record)
#------------------------------------------------------------------------------


###############################################################################
## CACHE STUFF
def delete_cached_putcodes():
    recid = raw_input('Which recid? ')
    redis_url = current_app.config.get('CACHE_REDIS_URL')
    r = StrictRedis.from_url(redis_url)
    key = 'orcidcache:{}:{}'.format(ORCID, recid)
    r.delete(key)
#------------------------------------------------------------------------------


###############################################################################
## DB STUFF
def _get_or_create_user_identity():
    user_identity = UserIdentity.query.get((ORCID, 'orcid'))
    print('Found UserIdentity={}'.format(user_identity))
    if not user_identity:
        user = User.query.filter_by(email=EMAIL).one_or_none()
        if not user:
            user = User(email=EMAIL)
            db.session.add(user)
            db.session.commit()
            print('Created User={}'.format(user))

        user_identity = UserIdentity(
            id=ORCID,
            id_user=user.id,
            method='orcid',
        )
        db.session.add(user_identity)
        db.session.commit()
        print('Created UserIdentity={}'.format(user_identity))
    return user_identity


def _get_or_create_remote_account(user):
    if user.remote_accounts:
        remote_account = user.remote_accounts[0]
        if not remote_account.extra_data['allow_push']:
            remote_account.extra_data['allow_push'] = True
            db.session.add(remote_account)
            db.session.commit()
        print('Found RemoteAccount={}'.format(remote_account))
    else:
        remote_account = RemoteAccount(
            user_id=user.id,
            client_id='0000-0001-8607-8906',  # Inspire client id.
            extra_data={
                'orcid': ORCID,
                'full_name': FULL_NAME,
                'allow_push': True,
            }
        )
        db.session.add(remote_account)
        db.session.commit()
        print('Created RemoteAccount={}'.format(remote_account))
    return remote_account


def _get_or_create_remote_token(remote_account):
    access_token = raw_input('Access token (see your tokens.local file)? ')
    if not access_token:
        print('Invalid access token')
        sys.exit(1)

    if remote_account.remote_tokens:
        remote_token = remote_account.remote_tokens[0]
        print('Found RemoteToken={}'.format(access_token))
    else:
        remote_token = RemoteToken(
            token_type='',
            remote_account=remote_account,
            access_token=access_token,  # Test user's token
            secret=None,
        )
        db.session.add(remote_token)
        db.session.commit()
        print('Created RemoteToken={}'.format(access_token))
    return remote_token


def get_or_create_db_token_data():
    user_identity = _get_or_create_user_identity()
    remote_account = _get_or_create_remote_account(user_identity.user)
    remote_token = _get_or_create_remote_token(remote_account)
    return remote_token, user_identity
#------------------------------------------------------------------------------


###############################################################################
## RECORD STUFF
def get_or_create_author_record():
    orcid_object = '[{"schema": "ORCID", "value": "%s"}]' % ORCID
    author_record = db.session.query(RecordMetadata)\
        .filter(type_coerce(RecordMetadata.json, JSONB)['ids'].contains(orcid_object)).one_or_none()

    if not author_record:
        # Create the author record.
        author_record = InspireRecord.create(get_author_json())
        author_record.commit()
        db.session.commit()
        print('Created Author record_metadata.id={}'.format(author_record.id))
    else:
        print('Found Author record_metadata.id={}'.format(author_record.id))

    return author_record

def make_doi_unique(record):
    """
    Args:
        record (InspireRecord)
    """
    doi = str(record['control_number'])[-4:].zfill(4)
    record['dois'][0]['value'] = record['dois'][0]['value'].replace('.1000/', '.{}/'.format(doi))

def get_or_create_literature_records(author_record, amount=1):
    # Get all records authored by this orcid.
    recids = get_literature_recids_for_orcid(ORCID)

    delta = amount - len(recids)
    if delta <= 0:
        print('Found {} records authored by this author, recids={}'.format(len(recids), recids))
        return recids

    for _ in range(delta):
        # Update author's recid in record.
        record_json = get_record_json()
        record_json['authors'][0]['record']['$ref'] = "{}/api/authors/{}".format(BASE_URL, author_record.json['control_number'])
        record = InspireRecord.create(record_json)
        record.commit()
        db.session.commit()

        make_doi_unique(record)
        record.commit()
        db.session.commit()

        print('Created new record authored by this author, recid={}'.format(record['control_number']))
        recids.append(record['control_number'])
    return recids


def setup_data():
    env = raw_input('Which env (local|qa|prod)? ')
    if env not in ENVS_BASEURLS.keys():
        print('Unknown env: {}'.format(env))
        sys.exit(1)

    global BASE_URL
    BASE_URL = ENVS_BASEURLS[env]
    print(BASE_URL)

    get_or_create_db_token_data()
    author_record = get_or_create_author_record()
    amt = raw_input('How many record do you need (authored by this author)? ')
    amt = int(amt)
    get_or_create_literature_records(author_record, amt)
#------------------------------------------------------------------------------


###############################################################################
## GET AUTHORED RECORDS
def get_authored_records():
    # Get all records authored by this orcid.
    recids = get_literature_recids_for_orcid(ORCID)
    print('Records authored by orcid={}: recids={}'.format(ORCID, recids))
#------------------------------------------------------------------------------


def main():
    answer = raw_input('What operation do you want to perform?\n'\
                       ' 1. setup data\n'\
                       ' 2. clean cache\n'\
                       ' 3. delete records\n'\
                       ' 4. print records recids authored by this author\n'\
                       'Answer: ')
    if answer not in ('1', '2', '3', '4'):
        print('Unknown answer: {}'.format(answer))
        sys.exit(1)

    if answer == '1':
        setup_data()
    elif answer == '2':
        delete_cached_putcodes()
    elif answer == '3':
        delete_record_by_pid()
    elif answer == '4':
        get_authored_records()
