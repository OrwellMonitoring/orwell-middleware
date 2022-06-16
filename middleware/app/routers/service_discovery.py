#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Authors: Gonçalo Leal (goncalolealsilva@ua.pt), Alexandre Serras (alexandreserras@ua.pt)
# Date: 02-04-2022

# Description:
# All service discovery related endpoints

import imp
from fastapi import APIRouter, Request
from app.config.settings import config

from sqlalchemy import select

from app.data.postgres import postgres_manager
from app.data.models.host import Host
from fastapi.responses import PlainTextResponse

from app.data.models.host_state import HostState

from app.config.settings import config


router = APIRouter()

@router.get("/service_discovery/targets/", tags=["targets"])
async def get_targets(request: Request):
    active_state = postgres_manager.get_by_name(HostState, 'ACTIVE')

    targets = postgres_manager.get_all_in(Host, Host.state_id, [active_state.id])
    targets.extend([Host('', '', '', host) for host in config.SD_ARTIFICIAL_HOSTS])
    
    return [
        {
            "targets": ["{}:{}".format(request.base_url.hostname, request.base_url.port)],
            "labels": {
                "__metrics_path__": "/metrics/" + str(target.ip),
                "__meta_datacenter": "IT Aveiro",
                "__meta_prometheus_job": "node"
            }
        }
        for target in targets
    ]

@router.get("/service_discovery/kafka/", tags=["kafka"], response_class=PlainTextResponse)
async def get_kafka_listener():
    # This endpoint is going to return the ip address of kafka listener 
    # DONT PUT THIS ON JSON
    return config.KAFKA_HOST+":"+config.KAFKA_LISTENER_PORT
