import ast
import pprint
import time

from . import states
from .client import FlowerClient


class FlowerOrcidTasksSearcher(object):
    def __init__(self, orcid, recid):
        self.flower = FlowerClient()
        self.orcid = orcid
        self.recid = int(recid)
        self.result = None

    def search(self, max_age=60*60*24*30):
        orcid_tasks_response = self.flower.get_tasks_orcid_push()
        orcid_tasks_response.raise_for_result()

        is_found = False
        for _, task_data in orcid_tasks_response.items():
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

    def _is_more_recent_than_current_result(self, task_data):
        if not self.result:
            return True
        received = task_data['received']
        result_received = self.result['received']
        return received > result_received

    def _is_more_recent_than_age(self, max_age, task_data):
        received = task_data['received']
        now = time.time()
        return received > now - max_age

    def _refresh_result_data(self):
        """
        NOTE: it would make more sense to use:
        self.flower.get_task_info(self.result['uuid'])
        but this call often gives a 500.
        """
        orcid_tasks_response = self.flower.get_tasks_orcid_push()
        orcid_tasks_response.raise_for_result()
        self.result = orcid_tasks_response[self.result['uuid']]

    def get_updated_result_state(self):
        self._refresh_result_data()
        return self.result['state']

    def is_updated_result_state_successful(self):
        return self.get_updated_result_state().upper() == 'SUCCESS'

    def is_updated_result_state_unsuccessful(self):
        return self.get_updated_result_state().upper() == 'FAILURE'

    def count_tasks_in_states(self, states):
        total_count = 0
        data = {}
        for state in states:
            orcid_tasks_response = self.flower.get_tasks_orcid_push(state=state, limit=0)
            orcid_tasks_response.raise_for_result()
            data[state] = len(orcid_tasks_response)
            total_count += len(orcid_tasks_response)
        data['total_count'] = total_count
        return data

    def count_tasks_in_unready_state(self):
        return self.count_tasks_in_states(states.UNREADY_STATES)

    def count_tasks_in_ready_state(self):
        return self.count_tasks_in_states(states.READY_STATES)

    def count_tasks_in_exception_state(self):
        return self.count_tasks_in_states(states.EXCEPTION_STATES)

    def count_tasks_in_failure_state(self):
        return self.count_tasks_in_states((states.FAILURE,))


def is_celery_task_orcid_push_successful(orcid, recid, timeout):
    searcher = FlowerOrcidTasksSearcher(orcid, recid)

    # Search for a task with that orcid, recid and not older than 1 min.
    # Do it for 1 minute.
    end_time = time.time() + 60
    while time.time() < end_time:
        if searcher.search(max_age=60):  # The task is valid if its ts is not older than 1 minute.
            break
        print('Recent celery orcid_push task not found for orcid={}, recid={}'.format(orcid, recid))
        time.sleep(2)

    if not searcher.result:
        return False

    # Wait for the task to be successful.
    end_time = time.time() + timeout
    while time.time() < end_time:
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
