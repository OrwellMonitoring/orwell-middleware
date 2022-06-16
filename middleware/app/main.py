import imp
import time
import json
import uvicorn
from threading import Thread
from datetime import datetime
from kafka import KafkaProducer

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import config
from app.config.docs import documentation_config
from app.config.cors import cors_config
from app.osm.osm_adapter import OSM_Adapter
from app.routers import metrics, service_discovery, db_helper, images, collectors, hosts, perfsonar
from app.data.postgres import postgres_manager

from sqlalchemy import select

from app.data.models.collector_type import CollectorType
from app.data.models.collector import Collector
from app.data.models.image import Image
from app.data.models.host_state import HostState
from app.gnocchi.gnocchi_puller import GnocchiPuller
from app.grafana_authorization.grafana_authorization import GrafanaAuthorizationMiddleware, GrafanaDashboard

app = FastAPI(**documentation_config)

app.add_middleware(
    CORSMiddleware,
    **cors_config
)

# Service Discovery
def service_discover_start():
    print("---------Initiating Service Discovery----------")
    osm_adapter = OSM_Adapter(config.OSM_HOST, config.OSM_USER, config.OSM_PWD, config.OSM_PROJECT)

    while True:
        time.sleep(30)
        new_vdus_ips = osm_adapter.get_vdus_ip()

# Service Discovery
def gnocchi_puller_start():
    print("---------Initiating Gnocchi Puller----------")
    gnocchi_puller = GnocchiPuller(config.OPENSTACK_HOST, config.OPENSTACK_ID, config.OPENSTACK_SECRET)

    producer = KafkaProducer(
        bootstrap_servers=['%s:%s' % (config.KAFKA_HOST, config.KAFKA_LISTENER_PORT)],
        value_serializer=lambda x: json.dumps(x).encode('utf-8')
    )

    while True:
        time.sleep(30)
        hosts = gnocchi_puller.get_gnocchi_targets()
        
        if hosts:
            for host in hosts:
                metrics_list = gnocchi_puller.get_metrics_list(host)

                metrics = {
                    "instance": host.ip
                }
                for metric_name, metric_id in metrics_list.items():
                    values = gnocchi_puller.get_metric_value(metric_id)
                    value = values[len(values) - 1]
                    
                    # Gnocchi's date
                    date = value[0].split('+')[0]
                    dt = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S")

                    # Actual date
                    actual_timestamp = time.time()

                    metrics[metric_name] = [
                        int(actual_timestamp),
                        value[1],
                        value[2]
                    ]

                print(metrics)
                # escrever no kafka
                producer.send('gnocchi', value=metrics)

# Initialize Database
def db_init():
    host_states = [
        HostState('ACTIVE'),
        HostState('INACTIVE'),
    ]
    postgres_manager.save_all(host_states)

    collectors_type = [
        CollectorType('PULL'),
        CollectorType('PUSH'),
    ]
    postgres_manager.save_all(collectors_type)

    pull = postgres_manager.get_by_name(CollectorType, 'PULL')
    push = postgres_manager.get_by_name(CollectorType, 'PUSH')

    collectors = [
        Collector('Prometheus', 'metrics', 9100, pull.id),
        Collector('Gnocchi', '', 0, pull.id),
        Collector('Telegraf', '', 0, push.id),
    ]
    postgres_manager.save_all(collectors)

    os_images = [
        Image('ubuntu_2004_5gasp_monitoring_prometheus'),
        Image('ubuntu_2004_5gasp_monitoring_telegraf'),
        Image('ubuntu-20.04-server-cloudimg-amd64')
    ]
    postgres_manager.save_all(os_images)

    image = postgres_manager.get_by_name(Image, 'ubuntu_2004_5gasp_monitoring_prometheus')
    prometheus = postgres_manager.get_by_name(Collector, 'Prometheus')

    image.collectors.append(prometheus)
    postgres_manager.commit()

    image = postgres_manager.get_by_name(Image, 'ubuntu_2004_5gasp_monitoring_telegraf')
    telegraf = postgres_manager.get_by_name(Collector, 'Telegraf')

    image.collectors.append(telegraf)
    postgres_manager.commit()

    image = postgres_manager.get_by_name(Image, 'ubuntu-20.04-server-cloudimg-amd64')
    gnocchi = postgres_manager.get_by_name(Collector, 'Gnocchi')

    image.collectors.append(gnocchi)
    postgres_manager.commit()

# Init Grafana Dashboard
GrafanaAuthorizationMiddleware.get_and_create_dashboard_for_user_if_not_exists(config.GRAFANA_USER, GrafanaDashboard.ESIGHT_INTERFACES)
GrafanaAuthorizationMiddleware.get_and_create_dashboard_for_user_if_not_exists(config.GRAFANA_USER, GrafanaDashboard.ESIGHT_SLOTS)

app.include_router(metrics.router)
app.include_router(service_discovery.router)
app.include_router(db_helper.router)
app.include_router(images.router)
app.include_router(collectors.router)
app.include_router(hosts.router)
app.include_router(perfsonar.router)

if not postgres_manager.get_by_name(CollectorType, 'PULL'):
    print("---------Initiating Empty DataBase----------")
    db_init()

# Threads
thread_service_discovery = Thread(target=service_discover_start)
thread_service_discovery.start()

time.sleep(5)

thread_gnocchi_puller = Thread(target=gnocchi_puller_start)
thread_gnocchi_puller.start()