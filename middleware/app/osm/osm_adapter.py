#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author: Gonçalo Leal (goncalolealsilva@ua.pt)
# Date: 07-04-2022

# Description:
# OSM Adapter to fetch VDU IPs

import time
import requests
import json

from app.osm.osm_exceptions import CouldNotLoginOnOSM

from app.data.postgres import postgres_manager
from app.data.models.host import Host
from app.data.models.image import Image
from app.data.models.host_state import HostState
from app.data.schemas.host import HostSchema
from app.data.models.collector import Collector

from app.grafana_authorization.grafana_authorization import GrafanaAuthorizationMiddleware, GrafanaDashboard

class OSM_Adapter:
    auth_token = ""
    expires_at = ""

    def __init__(self, ip, username, password, project_id) -> None:
        self.ip = ip
        self.username = username
        self.password = password
        self.project_id = project_id
        self.authenticate()

    # DECORATORS
    # Auth Decorator
    def requires_auth(func, *args, **kwargs):
        def wrapper(self, *args, **kwargs):
            try:
                self.update_auth_token()
                return func(self, *args, **kwargs)
            except Exception as e:
                print("Auth Required: To call this function you need to be authenticated in OSM! - " + str(e))
        return wrapper

    def authenticate(self):
        try:

            data = json.dumps({
                "username": self.username,
                "password": self.password,
                "project_id": self.project_id
            })

            response = requests.post(
                f"http://{self.ip}/osm/admin/v1/tokens",
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
            response_data = json.loads(response.text)
            self.auth_token = response_data["id"]
            self.expires_at = response_data["expires"]

        except:
            raise CouldNotLoginOnOSM(self.username, self.password, self.project_id)

    def update_auth_token(self):
        if self.auth_token == "" or self.expires_at < time.time():
            self.authenticate()

    @requires_auth
    def get_vdus_ip(self):
        # try:

        response = requests.get(
            f"http://{self.ip}/osm/nslcm/v1/vnf_instances",
            headers = {
                "Authorization": f"Bearer {self.auth_token}",
                'Accept': 'application/json'
            },
            timeout = 5
        )

        # check response status
        response.raise_for_status()

        # get data
        response_data = json.loads(response.text)
        osm_vnfs = [vnf_data for vnf_data in response_data if vnf_data["vdur"][0]["status"] == "ACTIVE"]

        # get saved Images (IDs only)
        saved_images = [image.name for image in postgres_manager.get_all(Image)]

        discovered_vnfs = {} # only the active ones
        for vnf in osm_vnfs:

            image_req = requests.get(
                f"http://{self.ip}/osm/vnfpkgm/v1/vnf_packages/{vnf['vnfd-id']}",
                headers = {
                    "Authorization": f"Bearer {self.auth_token}",
                    'Accept': 'application/json'
                },
                timeout = 5
            )
            image_req.raise_for_status()
            image_req_data = json.loads(image_req.text)

            image = image_req_data["sw-image-desc"][0]["id"]

            # check if the images exists in the database
            if image not in saved_images:
                postgres_manager.save_one(Image(image))
                
                image_obj = postgres_manager.get_by_name(Image, image)
                gnocchi = postgres_manager.get_by_name(Collector, 'Gnocchi')

                image_obj.collectors.append(gnocchi)
                postgres_manager.commit()

                saved_images.append(image)

            host_state = postgres_manager.get_by_name(HostState, 'ACTIVE')
            image_db = postgres_manager.get_by_name(Image, image)
            discovered_vnfs[vnf["id"]] = {
                "id": vnf["id"],
                "vim_id": vnf["vdur"][0]["vim-id"],
                "hostname": vnf["vnfd-ref"],
                "ip": vnf["ip-address"],
                "image_id": image_db.id,
                'state_id': host_state.id
            }

        # list of new VNFs (will remove the ones already saved on the database)
        discovered_ids = list(discovered_vnfs.keys())

        # list of all known VNF ids
        saved_ids = postgres_manager.get_all_ids(Host)

        for id in saved_ids:
            # convert uuid to string because osm only returns strings
            saved_id = str(id)

            # after looping through all the saved vnfs, the ones that do not belong 
            # to the dictionary are probably inactive
            host = postgres_manager.get_by_pk(Host, saved_id)

            if saved_id not in discovered_ids:               
                # change state to Inactive
                host_state = postgres_manager.get_by_name(HostState, 'INACTIVE')

                host = HostSchema(id=host.id, vim_id=host.vim_id, hostname=host.hostname, ip=host.ip, state_id=host_state.id)
                
            else:
                # get this VNF updated info
                osm_vnf = discovered_vnfs[saved_id]
                host = HostSchema(id=osm_vnf["id"], vim_id=osm_vnf["vim_id"], hostname=osm_vnf["hostname"], ip=osm_vnf["ip"], state_id=osm_vnf["state_id"])
                discovered_ids.remove(saved_id)

            postgres_manager.update_one(Host, host)

        # print("To Save:", discovered_ids)

        for id in discovered_ids:
            new_vnf = discovered_vnfs[id]

            developer_email = self.get_vnf_developer_email(new_vnf["vim_id"])
            GrafanaAuthorizationMiddleware.add_var_option_for_dashboard(developer_email, GrafanaDashboard.GENERAL, 2, new_vnf["ip"])

            postgres_manager.save_one(Host(new_vnf["id"], new_vnf["vim_id"], new_vnf["hostname"], new_vnf["ip"], new_vnf["image_id"], new_vnf["state_id"]))

        return discovered_vnfs

        # except:
        #     raise CouldNotLoginOnOSM(self.username, self.password, self.project_id)


    def get_vnf_developer_email(self, vim_id) -> str:
        developers = [
        'pedro.dld@av.it.pt',
        'vascoregal@av.it.pt',
        'alexandreserras@av.it.pt',
        'goncalolealsilva@av.it.pt'
        ]

        return developers[postgres_manager.get_count(Host)%len(developers)]