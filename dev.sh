#!/bin/bash

docker-compose down > /dev/null
docker-compose build > /dev/null
docker-compose up -d redis postgres kafka zookeeper > /dev/null

export $(xargs < .env)
export KAFKA_HOST=localhost

# while ! docker-compose exec redis $(redis-cli ping); do sleep 1; done

pip install -r middleware/requirements.txt

cd middleware; uvicorn app.main:app --reload
