FROM debian:9

ENV DSS_VERSION="4.2.2" \
    DSS_DATADIR="/home/dataiku/dss" \
    DSS_PORT=10000

# Dataiku account and data dir setup
RUN useradd -s /bin/bash dataiku \
    && mkdir -p /home/dataiku ${DSS_DATADIR} \
    && chown -Rh dataiku:dataiku /home/dataiku ${DSS_DATADIR}

# System dependencies
# TODO - much could be removed by building externally the required R packages
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        file \
        locales \
        procps \
        acl \
        curl \
        git \
        libexpat1 \
        nginx \
        unzip \
        zip \
        default-jre-headless \
        python2.7 \
        libpython2.7 \
        libfreetype6 \
        libgfortran3 \
        libgomp1 \
        r-base-dev \
        r-recommended \
        libicu-dev \
        libcurl4-openssl-dev \
        libssl-dev \
        libxml2-dev \
        libzmq3-dev \
        pkg-config \
        python2.7-dev \
    && rm -rf /var/lib/apt/lists/* \
    && localedef -f UTF-8 -i en_US en_US.UTF-8

# Download and extract DSS kit
RUN DSSKIT="dataiku-dss-$DSS_VERSION" \
    && cd /home/dataiku \
    && echo "+ Downloading kit" \
    && curl -OsS "https://downloads.dataiku.com/public/studio/$DSS_VERSION/$DSSKIT.tar.gz" \
    && echo "+ Extracting kit" \
    && tar xf "$DSSKIT.tar.gz" \
    && rm "$DSSKIT.tar.gz" \
    && echo "+ Compiling Python code" \
    && python2.7 -m compileall -q "$DSSKIT"/python "$DSSKIT"/dku-jupyter \
    && { python2.7 -m compileall -q "$DSSKIT"/python.packages >/dev/null || true; } \
    && chown -Rh dataiku:dataiku "$DSSKIT"

# Install required R packages
RUN R --slave --no-restore \
    -e "install.packages(c('httr', 'RJSONIO', 'dplyr', 'IRkernel', 'sparklyr', 'ggplot2', 'gtools', 'tidyr', 'rmarkdown'), \
                        repos=c('file:///home/dataiku/dataiku-dss-$DSS_VERSION/dku-jupyter/R', \
                                'https://cloud.r-project.org'))"

# Entry point
WORKDIR /home/dataiku
USER dataiku

COPY run.sh /home/dataiku/

EXPOSE $DSS_PORT

CMD [ "/home/dataiku/run.sh" ]
