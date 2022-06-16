import secrets
import string
import json
import os

import requests
from requests.structures import CaseInsensitiveDict

from app.config.settings import config


# TODO Improve logging strategy (the logging module is not working)
class GrafanaLogging:

  def info(self, msg: str):
    print(msg)

  
logging = GrafanaLogging()


# This class works as an enum for the available dashboards
# The string values should be the name of existent json 
# files insiside of the `dashboards` folder
class GrafanaDashboard:

  GENERAL = 'general'
  PERFSONAR = 'perfsonar'
  ESIGHT_INTERFACES = 'esight_interfaces'
  ESIGHT_SLOTS = 'esight_slots'


# Class composed of static functions that abstract the 
# interaction with the json of the dashboards
class GrafanaDashboardsUtils:

  DASHBOARDS_PATH = './app/grafana_authorization/dashboards'

  # Loads a dashboards json
  # Optionally replaces `#ds_uid#` with a specified data source id, 
  # which is required for sending the object to the Grafana API
  #
  # dashboard: str - Name of the dashboard, which usually would come from GrafanaDashboard enum
  # data_source_uid: str = None - uid of the Grafana's datasource. The json file should 
  # have `#ds_uid#` where the replacement is required
  #
  # returns dict - contents from the json file
  @classmethod
  def get_dashboard(cls, dashboard: str, data_source_uid: str = None) -> dict:
    dashboard_file_name = dashboard + '.json'
    dashboard_file = cls.DASHBOARDS_PATH + '/' + dashboard_file_name
    dashboard = None

    if dashboard_file_name in os.listdir(cls.DASHBOARDS_PATH):
      with open(dashboard_file, 'r') as f:
        dashboard = f.read()
        if data_source_uid is not None: dashboard = dashboard.replace('#ds_uid#', data_source_uid)
        dashboard = json.loads(dashboard)

    if dashboard is None: logging.info("Grafana dashboard '{}' could not be loaded from disk".format(dashboard))

    return dashboard

  # Updates a specific variable from the dashboard dictionary
  #
  # dashboard: dict - Dictionary which may come from the json file
  # var_idx: int - Index of the variable that must be updated
  # values: dict - Dictionary with label: value pairs
  @classmethod
  def update_dashboard_variable(cls, dashboard: dict, var_idx: int, values: dict):
    var = dashboard['templating']['list'][var_idx]

    var['query'] = ','.join(['{} : {}'.format(label, value) for value, label in values.items()])
    var['options'] = [{ "selected": False, "text": label, "value": value } for value, label in values.items()]

    first_option = var['options'][0]
    first_option['selected'] = True
    dashboard['templating']['list'][var_idx]['current'] = first_option

  # Adds an option to a dashboard variable
  #
  # dashboard: dict - Dictionary which may come from the json file
  # var_idx: int - Index of the variable that must be updated
  # value: str - Option value
  # label: str = None - Optional label for the option. If not specified it is the same as value
  @classmethod
  def add_dashboard_variable_option(cls, dashboard: dict, var_idx: int, value: str, label: str = None):
    current_options = { option['value']: option['text'] for option in dashboard['templating']['list'][var_idx]['options'] }
    cls.update_dashboard_variable(dashboard, var_idx, { **current_options, value: label if label is not None else value })

  # Get the dashboard identifier from the json file
  # Each json file has a uid field, which must be unique and identifies the dashboard
  #
  # dashboard: str - Name of the dashboard, which usually would come from GrafanaDashboard enum
  #
  # returns str - dashboard uid
  @classmethod
  def get_dashboard_uid(cls, dashboard: str) -> str:
    dashboard = cls.get_dashboard(dashboard)
    return dashboard.get('uid')


# This class removes the repetion of using Python's requests
# module for the Grafana API, mainly the authentication
class GrafanaRequests:

  GRAFANA_API_URL = "http://{}:{}/api".format(config.GRAFANA_HOST, config.GRAFANA_PORT)

  def request(self, func, url: str, params=None):
    if params is None: params = {}
    return func(self.GRAFANA_API_URL + url, **params, auth=(config.GRAFANA_USER, config.GRAFANA_PWD))

  def get(self, url: str, params={}):
    return self.request(requests.get, url, { "params": params })

  def post(self, url: str, json={}):
    return self.request(requests.post, url, { "json": json })


# Actual Grafana API's wrapper
class GrafanaAuthorization:

  PASSWORD_SIZE = 10

  def __init__(self) -> None:
      self.requests = GrafanaRequests()

  # Generates a random password for a Grafana user
  #
  # returns str - Generated password
  def gen_password(self) -> str:
    return 'admin'

    # TODO Generating a random password can be implemented when we're able to send it via email
    # characters = string.ascii_letters + string.digits + string.punctuation
    # return ''.join([ secrets.choice(characters) for _ in range(self.PASSWORD_SIZE) ])

  # Get the organization associated with an user
  #
  # email: str - Usually user's email, but username will also work
  # 
  # returns int - organization identifier
  def get_user_organization_id(self, email: str) -> int:
    req = self.requests.get("/users/lookup", { "loginOrEmail": email })
    oid = req.json().get('orgId')

    if oid is None:
      username = email.split('@')[0]

      oid = self.create_organization(username)

      self.create_data_source()

      req = self.requests.post("/admin/users", { "name": username, "login": username, "email": email, "password": self.gen_password(), "OrgId": oid })
      if req.status_code != 200: oid = None

    logging.info("Grafana OID for user '{}' is {}".format(email, oid))

    return oid

  # Create an organization associated with an user
  #
  # email: str - Usually user's email, but username will also work
  # 
  # returns int - organization identifier
  def create_organization(self, email: str) -> int:
    req = self.requests.post("/orgs", { "name": email })
    oid = req.json().get('orgId')

    logging.info("Grafana OID for user '{}' is {}".format(email, oid))

    self.add_user_to_organization(oid, config.GRAFANA_USER)
    self.set_active_organization(oid)

    return oid

  # Gives an user access to specified organization
  #
  # oid: int - Organization id
  # user: str - Usually user's email, but username will also work
  # 
  # returns bool - operation success
  def add_user_to_organization(self, oid: int, user: str) -> bool:
    req = self.requests.post("/orgs/{}/users".format(oid), { "loginOrEmail": user, "role": "Admin" })
    return req.status_code == 200

  # Sets the currently active organization. This will affect subsequent requests
  #
  # oid: int - Organization id
  # 
  # returns bool - operation success
  def set_active_organization(self, oid: int) -> bool:
    req = self.requests.post("/user/using/{}".format(oid))
    return req.status_code == 200

  # Adds dashboard to an user's main organization
  #
  # email: str - Usually user's email, but username will also work
  # dashboard_name: str - Name of the dashboard, which usually would come from GrafanaDashboard enum
  # 
  # returns bool - operation success
  def get_and_create_dashboard_for_user_if_not_exists(self, email: str, dashboard_name: str) -> bool:
    oid = self.get_user_organization_id(email)
    self.set_active_organization(oid)

    uid = GrafanaDashboardsUtils.get_dashboard_uid(dashboard_name)
    req = self.requests.get("/dashboards/uid/{}".format(uid))

    if req.status_code == 200: return True

    dashboard = GrafanaDashboardsUtils.get_dashboard(dashboard_name, self.get_datasource_uid())

    req = self.requests.post("/dashboards/db", { "dashboard": dashboard })
    success = req.status_code == 200

    return success

  # Adds an option to a dashboard inside of an user's main organization
  #
  # email: str - Usually user's email, but username will also work
  # dashboard_name: str - Name of the dashboard, which usually would come from GrafanaDashboard enum
  # var_idx: int - Index of the variable that must be updated
  # value: str - Option value
  # label: str = None - Optional label for the option. If not specified it is the same as value
  # 
  # returns bool - operation success
  def add_var_option_for_dashboard(self, email: str, dashboard_name: str, var_idx: int, value: str, label: str = None) -> bool:
    self.get_and_create_dashboard_for_user_if_not_exists(email, dashboard_name)

    uid = GrafanaDashboardsUtils.get_dashboard_uid(dashboard_name)
    req = self.requests.get("/dashboards/uid/{}".format(uid))

    dashboard = req.json().get('dashboard')
    GrafanaDashboardsUtils.add_dashboard_variable_option(dashboard, var_idx, value, label)

    return self.create_or_update_dashboard(dashboard)

  # Creates or updates a dashboard in Grafana
  #
  # dashboard: dict - Dictionary which may come from the json file
  # 
  # returns bool - operation success
  def create_or_update_dashboard(self, dashboard: dict) -> bool:
    req = self.requests.post("/dashboards/db", { "dashboard": dashboard })
    success = req.status_code == 200

    return success

  # Creates the Prometheus data source inside of Grafana
  # 
  # returns bool - operation success
  def create_data_source(self) -> bool:
    req = self.requests.post("/datasources", { "name":"Prometheus", "type":"prometheus", "url":"http://{}:{}".format(config.PROMETHEUS_HOST, config.PROMETHEUS_PORT), "basicAuth": False, "access":"proxy" })
    success = req.status_code == 200
    
    return success

  # Gets Prometheus datasource's identifier for Grafana
  # If said datasource does not exist it will be created
  # 
  # returns int - datasource identifier
  def get_datasource_uid(self) -> int:
    req = self.requests.get("/datasources")
    sources = req.json()

    success = req.status_code == 200 and type(sources) == list

    if len(sources) == 0:
      self.create_data_source()
      return self.get_datasource_uid()

    if success: return sources[0]["uid"]
    return success


GrafanaAuthorizationMiddleware = GrafanaAuthorization()
