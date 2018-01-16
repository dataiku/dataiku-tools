#!/bin/bash -e

docker stop dataiku && docker rm -v dataiku
docker build . -t gcr.io/retailcatalyst-187519/crs-dataiku:4.1.0-hadoop
docker run --name dataiku -d gcr.io/retailcatalyst-187519/crs-dataiku:4.1.0-hadoop
docker exec -it dataiku bash
