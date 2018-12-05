import backoff

import config
from inspire_service_orcid.client import OrcidClient


def delete_work(orcid, token, recid):
    putcode = get_putcode_for_work(orcid, token, recid)
    if putcode:
        client = OrcidClient(token, orcid)
        client.delete_work(putcode)


def get_putcode_for_work(orcid, token, recid):
    client = OrcidClient(token, orcid)
    response = client.get_all_works_summary()
    response.raise_for_result()
    source_client_id_path = config.get('orcid-api', 'consumer_key')
    putcodes = list(response.get_putcodes_for_source(source_client_id_path))

    if not putcodes:
        return None

    # TODO: this has to be simplified when we push recids as external
    # identifier (thus just the get_all_works_summary() call is required to
    # match recids with putcodes).
    for response in client.get_bulk_works_details_iter(putcodes):
        response.raise_for_result()
        for putcode, url in response.get_putcodes_and_urls():
            if url.endswith('/{}'.format(recid)):
                return putcode


@backoff.on_exception(backoff.expo, AssertionError, max_time=60)
def assert_any_putcode_for_work(orcid, token, recid):
    assert get_putcode_for_work(orcid, token, recid)

@backoff.on_exception(backoff.expo, AssertionError, max_time=60)
def assert_no_putcode_for_work(orcid, token, recid):
    assert not get_putcode_for_work(orcid, token, recid)
