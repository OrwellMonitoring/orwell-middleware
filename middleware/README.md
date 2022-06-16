# Orwell's Middleware API

## Environment Variables

- **`REDIS_HOST`**:
    - **Description:** Address running the Redis instance where metrics are stored.
    - **Type:** `string`
    - **Default:** `"localhost"`

- **`REDIS_PORT`**:
    - **Description:** Port running the Redis instance.
    - **Type:** `int`
    - **Default:** `6379`

- **`REDIS_PASSWORD`**:
    - **Description:** Password for the Redis instance.
    - **Type:** `string`
    - **Default:** `"root"`

- **`POSTGRES_HOST`**:
    - **Description:** Address running the Postgres instance where the host configuration is stored.
    - **Type:** `string`
    - **Default:** `"localhost"`

- **`POSTGRES_PORT`**:
    - **Description:** Port running the Postgres instance.
    - **Type:** `int`
    - **Default:** `5432`

- **`POSTGRES_DB`**:
    - **Description:** Default database for the Postgres instance.
    - **Type:** `string`
    - **Default:** `"orwell_hosts"`

- **`POSTGRES_USER`**:
    - **Description:** User for the Postgres instance.
    - **Type:** `string`
    - **Default:** `"postgres"`

- **`POSTGRES_PASSWORD`**:
    - **Description:** Password for the Postgres instance.
    - **Type:** `string`
    - **Default:** `"root"`

- **`KAFKA_HOST`**:
    - **Description:** Address running the Kafka instance that receives unprocessed metrics.
    - **Type:** `string`

- **`KAFKA_PORT`**:
    - **Description:** Port running the Kafka instance.
    - **Type:** `int`

- **`OSM_HOST`**:
    - **Description:** Address running the Open Source Mano.
    - **Type:** `string`

- **`OSM_USER`**:
    - **Description:** User for the Open Source Mano.
    - **Type:** `string`

- **`OSM_PWD`**:
    - **Description:** Password for the Open Source Mano.
    - **Type:** `string`

- **`OSM_PROJECT`**:
    - **Description:** Project identifier inside of the Open Source Mano.
    - **Type:** `string`

- **`OPENSTACK_HOST`**:
    - **Description:** Address running OpenStack.
    - **Type:** `string`

- **`OPENSTACK_ID`**:
    - **Description:** OpenStack's identifier.
    - **Type:** `string`

- **`OPENSTACK_SECRET`**:
    - **Description:** OpenStack's secret.
    - **Type:** `string`

- **`PROMETHEUS_HOST`**:
    - **Description:** Address running the Prometheus instance.
    - **Type:** `string`

- **`PROMETHEUS_PORT`**:
    - **Description:** Port running the Prometheus instance.
    - **Type:** `int`
    - **Default:** `9090`

- **`GRAFANA_HOST`**:
    - **Description:** Address running the Grafana instance.
    - **Type:** `string`

- **`GRAFANA_PORT`**:
    - **Description:** Port running the Grafana instance.
    - **Type:** `int`
    - **Default:** `3000`

- **`PERFSONAR_HOST`**:
    - **Description:** Address running the PerfSonar Toolkit instance.
    - **Type:** `string`

- **`PERFSONAR_VERIFY_SSL`**:
    - **Description:** Whether to verify the SSL certificate for the running the PerfSonar Toolkit instance.
    - **Type:** `bool`
    - **Default:** `False`

- **`SD_ARTIFICIAL_HOSTS`**:
    - **Description:** Additional entries for the service discovery endpoint.
    - **Type:** `json list`
    - **Default:** `"[]"`
