from pydantic import BaseSettings

class Settings(BaseSettings):

    # REDIS ENV
    REDIS_HOST: str = 'localhost'
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = 'root'

    # POSTGRES ENV
    POSTGRES_HOST: str = 'localhost'
    POSTGRES_DB: str = 'orwell_hosts'
    POSTGRES_USER: str = 'postgres'
    POSTGRES_PASSWORD: str = 'root'
    POSTGRES_PORT: int = 5432

    # KAFKA ENV
    KAFKA_HOST:str
    KAFKA_LISTENER_PORT: str

    # OSM ENV
    OSM_HOST: str
    OSM_USER: str
    OSM_PWD: str
    OSM_PROJECT: str

    # OpenStack ENV
    OPENSTACK_HOST: str
    OPENSTACK_ID: str
    OPENSTACK_SECRET: str

    # Prometheus ENV
    PROMETHEUS_HOST: str
    PROMETHEUS_PORT: int = 9090

    # Grafana ENV
    GRAFANA_HOST: str
    GRAFANA_PORT: int = 3000
    GRAFANA_USER: str = 'admin'
    GRAFANA_PWD: str = 'admin'

    # PerfSonar ENV
    PERFSONAR_HOST: str
    PERFSONAR_HOST_LABEL: str = 'Local'
    PERFSONAR_VERIFY_SSL: bool = False

    # Artificial hosts for metrics that are not associated with VMs
    SD_ARTIFICIAL_HOSTS: list = []

config = Settings()
