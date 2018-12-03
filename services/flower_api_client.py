import ast
import time
from pprint import pprint

from service_flower.client import FlowerClient


def is_orcid_push_task_successful(orcid, recid, timeout):
    searcher = FlowerOrcidTasksSearcher(orcid, recid)

    # Search for a task with that orcid, recid and not older than 1 min.
    # Do it for 1 minute.
    start_time = time.time()
    while time.time() < start_time + 60:
        if searcher.search(max_age=60):  # The task is valid if its ts is not older than 1 minute.
            break
        print('Recent celery orcid_push task not found for orcid={}, recid={}'.format(orcid, recid))
        time.sleep(2)

    if not searcher.result:
        return False

    # Wait for the task to be successful.
    start_time = time.time()
    while time.time() < start_time + timeout:
        # state: FAILURE.
        if searcher.is_updated_result_state_unsuccessful():
            print('Celery task id={} failed:\n{}'.format(
                searcher.result['uuid'],
                pprint.pformat(searcher.result)
            ))
            return False
        # state: SUCCESS.
        if searcher.is_updated_result_state_successful():
            print('Celery task id={} successful'.format(
                searcher.result['uuid'], searcher.result['state']
            ))
            return True
        # state: other.
        print('Celery task id={} not successful yet (state={})'.format(
                searcher.result['uuid'], searcher.result['state']
        ))
        time.sleep(2)

    return False


class FlowerOrcidTasksSearcher(object):
    def __init__(self, orcid, recid):
        self.client = FlowerClient()
        self.orcid = orcid
        self.recid = int(recid)
        self.result = None

    def search(self, max_age):
        response = self.client.get_tasks(taskname='inspirehep.modules.orcid.tasks.orcid_push')
        response.raise_for_result()

        is_found = False
        for _, task_data in response.items():
            if (self._is_match(task_data) and \
                    self._is_more_recent_than_age(max_age, task_data) and \
                    self._is_more_recent_than_current_result(task_data)):
                self.result = task_data
                is_found = True
        return is_found

    def _is_match(self, task_data):
        kwargs = task_data['kwargs']
        # `kwargs` is now a dictionary encoded as a string,
        # Format: u"{'orcid': '0000-0002-2027-1428', 'oauth_token': '6c350cac-9cd9-408d-a47d-93064691f254', 'rec_id': 1676179}"
        kwargs = ast.literal_eval(kwargs)
        return (kwargs['orcid'] == self.orcid and
                int(kwargs['rec_id']) == self.recid)

    def _is_more_recent_than_age(self, max_age, task_data):
        received = task_data['received']
        now = time.time()
        return received > now - max_age

    def _is_more_recent_than_current_result(self, task_data):
        if not self.result:
            return True
        received = task_data['received']
        result_received = self.result['received']
        return received > result_received

    def is_updated_result_state_successful(self):
        return self.get_updated_result_state().upper() == 'SUCCESS'

    def is_updated_result_state_unsuccessful(self):
        return self.get_updated_result_state().upper() == 'FAILURE'

    def get_updated_result_state(self):
        self._refresh_result_data()
        return self.result['state']

    def _refresh_result_data(self):
        """
        NOTE: it would make more sense to use:
        self.flower.get_task_info(self.result['uuid'])
        but this call often gives a 500.
        """
        response = self.client.get_tasks(taskname='inspirehep.modules.orcid.tasks.orcid_push')
        response.raise_for_result()
        self.result = response[self.result['uuid']]
