# Standard Dataiku DSS Dockerfile

This directory contains the Dockerfile which is used by Dataiku to build the standard docker images for DSS.

To rebuild, run:
    docker build --build-arg dssVersion=DSS_VERSION .

where DSS_VERSION is the DSS version to use, e.g. "6.0.0".
