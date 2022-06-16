#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author: Gonçalo Leal (goncalolealsilva@ua.pt)
# Date: 07-04-2022

# Description:
# OSM Adapter to fetch VDU IPs

import time
import json
import requests
import datetime

from sqlalchemy import select

from app.data.postgres import postgres_manager
from app.data.models.host import Host
from app.data.models.image import Image
from app.data.models.host_state import HostState
from app.gnocchi.gnocchi_exceptions import CouldNotLoginGnocchi
from app.data.models.collector import Collector

class GnocchiPuller:
    auth_token = ""
    expires_at = ""

    def __init__(self, ip, id, secret):
        self.ip = ip
        self.id = id
        self.secret = secret

        self.authenticate()

    # DECORATORS
    # Auth Decorator
    def requires_auth(func, *args, **kwargs):
        def wrapper(self, *args, **kwargs):
            try:
                self.update_auth_token()
                return func(self, *args, **kwargs)
            except Exception as e:
                print("Auth Required: To call this function you need to be authenticated! - " + str(e))
        return wrapper

    def authenticate(self):
        try:

            data = json.dumps({
                "auth": {
                    "identity": {
                        "methods": [
                            "application_credential"
                        ],
                        "application_credential": {
                            "id": self.id,
                            "secret": self.secret
                        }
                    }   
                }
            })

            response = requests.post(
                f"http://{self.ip}/identity/v3/auth/tokens?nocatalog",
                headers = {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                data = data,
                timeout = 5
            )

            # check response status
            response.raise_for_status()

            # get data
            response_text = json.loads(response.text)
            self.auth_token = response.headers["X-Subject-Token"]
            date_str = response_text["token"]["expires_at"].split('.')[0]

            date_time_obj = datetime.datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S')

            self.expires_at = date_time_obj.timestamp()

        except:
            raise CouldNotLoginGnocchi(self.id, self.secret)

    def update_auth_token(self):
        if self.auth_token == "" or float(self.expires_at) < time.time():
            self.authenticate()

    @requires_auth
    def get_gnocchi_targets(self):
        gnocchi = postgres_manager.get_by_name(Collector, 'Gnocchi')

        query = select(Image.id).where(Image.collectors.contains(gnocchi))
        result = postgres_manager.execute(query)

        images = []
        for res in result:
            images.append(res[0])

        all_images = set(postgres_manager.get_all(Image))

        img_with_collectors = set(postgres_manager.get_all_join(Image, Host))

        img_without_collectors = all_images.difference(img_with_collectors)

        for img in img_without_collectors:
            images.append(img.id)

        hosts = postgres_manager.get_all_in(Host, Host.image_id, images)

        print(hosts)

        if hosts == None:
            return []

        return hosts

    @requires_auth
    def get_metrics_list(self, host):

        response = requests.get(
            f"http://{self.ip}/metric/v1/resource/instance/{host.vim_id}",
            headers = {
                "X-Auth-Token": f"{self.auth_token}",
                'Accept': 'application/json'
            },
            timeout = 5
        )

        response_text = json.loads(response.text)

        if "metrics" in response_text:
            return response_text["metrics"]
        else:
            return {}

    @requires_auth
    def get_metric_value(self, metric_id):
        response = requests.get(
            f"http://{self.ip}/metric/v1/metric/{metric_id}/measures",
            headers = {
                "X-Auth-Token": f"{self.auth_token}",
                'Accept': 'application/json'
            },
            timeout = 5
        )

        response_text = json.loads(response.text)
        return response_text