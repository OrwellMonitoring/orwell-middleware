import json
import requests
from requests.exceptions import ConnectTimeout

from app.config.settings import config
from ..grafana_authorization.grafana_authorization import GrafanaAuthorizationMiddleware, GrafanaDashboard


# TODO Improve logging strategy (the logging module is not working)
class PerfsonarLogging:

  def info(self, msg: str):
    print(msg)

  
logging = PerfsonarLogging()


# This class removes the repetion of using Python's requests
# module for the PerfSonar API
class PerfsonarRequests:

  PERFSONAR_API_URL = "https://" + config.PERFSONAR_HOST + "/pscheduler"

  def request(self, func, url: str, params=None):
    if params is None: params = {}
    return func(self.PERFSONAR_API_URL + url, **params, verify=config.PERFSONAR_VERIFY_SSL)

  def get(self, url: str, params={}):
    return self.request(requests.get, url, { "params": params })

  def post(self, url: str, json={}):
    return self.request(requests.post, url, { "json": json })


# Actual PerfSonar API's wrapper
class PerfsonarWrapper:

  def __init__(self) -> None:
    self.requests = PerfsonarRequests()
    GrafanaAuthorizationMiddleware.add_var_option_for_dashboard(config.GRAFANA_USER, GrafanaDashboard.PERFSONAR, 0, config.PERFSONAR_HOST, config.PERFSONAR_HOST)

  # Get a valid test object from the command-line arguments
  #
  # type: str - Test type, as mentioned in the [docs](https://docs.perfsonar.net/pscheduler_ref_tests_tools.html)
  # 
  # returns dict - test schema
  def task_args_to_schema(self, type: str, args: list) -> dict:
    return self.requests.get(f"/tests/{type}/spec", { "args": json.dumps(args) }).json()

  # Load desired configuration from the config file
  #
  # address: str - Destination address for the tests
  # 
  # returns list - task_list, schedule_config, archive_config
  def get_tasks_info (self, address: str) -> list:
    with open('./app/perfsonar/config.json', 'r') as f:
      info = json.load(f)
      
    for i in range(len(info['tasks'])):
      info['tasks'][i]['args'].extend(['--dest', address])

    return list(info.values())

  # Configure tests for a new node
  #
  # address: str - Address value
  # label: str - Address label
  # 
  # returns bool - operation success
  def add_node (self, address: str, label: str = None) -> bool:

    # Check if `address` is a valid PerfSonar node
    try:
      requests.get(f"https://{address}/pscheduler/", verify=config.PERFSONAR_VERIFY_SSL, timeout=3)
      logging.info('Address is a valid PerfSonar Host!')
    except ConnectTimeout:
      logging.info('Address is not a valid PerfSonar Host!')
      return False

    if label is None: label = address

    tasks, schedule, archive = self.get_tasks_info(address)

    GrafanaAuthorizationMiddleware.add_var_option_for_dashboard(config.GRAFANA_USER, GrafanaDashboard.PERFSONAR, 1, address, label)

    for task in tasks:
      task_definition = {
        "test": {
          "type": task['type'],
          "spec": self.task_args_to_schema(task['type'], task['args'])
        },
        "schedule": schedule,
        "archives": [ archive ]
      }

      logging.info(f"Creating task for {task['type']} test...")
      logging.info("Output: " + self.requests.post("/tasks", task_definition).text)
      
    return True


PerfsonarMiddleware = PerfsonarWrapper()
