import requests

import config

from .models import FlowerResponse


class FlowerClient(object):
    def __init__(self):
        self.base_url = 'https://inspire-qa-worker3-task1.cern.ch/api'
        # self.base_url = 'https://inspire-prod-worker3-task1.cern.ch/api'

    def get_tasks(self, taskname='', limit=25):
        """
        Example:

        $ curl -k "https://inspire-prod-worker3-task1.cern.ch/api/tasks?taskname=inspirehep.modules.orcid.tasks.orcid_push&limit=10" -u username:password | jq
          % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                         Dload  Upload   Total   Spent    Left  Speed
        100   857  100   857    0     0  17907      0 --:--:-- --:--:-- --:--:-- 18234
        {
          "fa929218-b49d-44e9-a5a3-8a94c8e0ca29": {
            "root_id": "fa929218-b49d-44e9-a5a3-8a94c8e0ca29",
            "result": "None",
            "children": [],
            "uuid": "fa929218-b49d-44e9-a5a3-8a94c8e0ca29",
            "clock": 167456,
            "exchange": null,
            "routing_key": null,
            "failed": null,
            "state": "SUCCESS",
            "client": null,
            "parent_id": null,
            "kwargs": "{'orcid': '0000-0002-0942-3697', 'oauth_token': '98674ecf-8ad4-466b-bd4e-ab40dec87168', 'rec_id': 1678462}",
            "sent": null,
            "expires": null,
            "parent": null,
            "retries": 0,
            "started": 1531213555.923144,
            "timestamp": 1531213557.500176,
            "args": "()",
            "rejected": null,
            "name": "inspirehep.modules.orcid.tasks.orcid_push",
            "received": 1531213263.680338,
            "exception": null,
            "revoked": null,
            "succeeded": 1531213557.500176,
            "traceback": null,
            "eta": null,
            "retried": null,
            "runtime": 1.5760211059823632,
            "root": "fa929218-b49d-44e9-a5a3-8a94c8e0ca29"
          }
        }
        """
        endpoint = 'tasks'
        query = 'taskname={}'.format(taskname) if taskname else ''
        query += '&limit={}'.format(limit) if limit else ''
        url = '{}/{}?{}'.format(self.base_url, endpoint, query)

        username = config.get('flower-api-httpauth-prod', 'username')
        password = config.get('flower-api-httpauth-prod', 'password')
        response = requests.get(url, verify=False, auth=(username, password))
        return FlowerResponse(response)

    def get_tasks_orcid_push(self, limit=25):
        return self.get_tasks(taskname='inspirehep.modules.orcid.tasks.orcid_push', limit=limit)

    def get_task_info(self, task_id):
        """
        Example:

        $ curl -u inspire:inspire -k "https://inspire-prod-worker3-task1.cern.ch/api/task/info/7d4d92db-39d0-4918-bd86-7ec243ba008d" | jq
          % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                         Dload  Upload   Total   Spent    Left  Speed
        100   910  100   910    0     0  23293      0 --:--:-- --:--:-- --:--:-- 23333
        {
          "root_id": "b4931472-3150-49a2-b33a-ea97d15190dd",
          "result": null,
          "children": [],
          "uuid": "7d4d92db-39d0-4918-bd86-7ec243ba008d",
          "clock": 7258101,
          "exchange": null,
          "routing_key": null,
          "failed": null,
          "state": "STARTED",
          "client": null,
          "parent_id": "b4931472-3150-49a2-b33a-ea97d15190dd",
          "kwargs": "{'orcid': '0000-0002-2064-2954', 'oauth_token': '846a175b-416a-470e-9a38-9b777389251a', 'rec_id': 1261966}",
          "sent": null,
          "expires": null,
          "parent": "b4931472-3150-49a2-b33a-ea97d15190dd",
          "retries": 0,
          "started": 1531321917.734636,
          "timestamp": 1531321917.734636,
          "args": "()",
          "worker": "celery@inspire-prod-worker3-task5.cern.ch",
          "rejected": null,
          "name": "inspirehep.modules.orcid.tasks.orcid_push",
          "received": 1531321484.761342,
          "exception": null,
          "revoked": null,
          "succeeded": null,
          "traceback": null,
          "eta": null,
          "retried": null,
          "runtime": null,
          "root": "b4931472-3150-49a2-b33a-ea97d15190dd"
        }

        NOTE 2019-07: oftne this call gives a 500 even for a task_id that
        is correctly shown in the get_tasks() call.
        """
        endpoint = 'task/info'
        url = '{}/{}/{}'.format(self.base_url, endpoint, task_id)

        username = config.get('flower-api-httpauth-prod', 'username')
        password = config.get('flower-api-httpauth-prod', 'password')
        response = requests.get(url, verify=False, auth=(username, password))
        return FlowerResponse(response)
