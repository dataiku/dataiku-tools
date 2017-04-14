FROM debian:8

ENV DSS_VERSION="4.0.3" \
    DSS_DATADIR="/home/dataiku/dss" \
    DSS_PORT=10000

# Dataiku account and data dir setup
RUN useradd -s /bin/bash dataiku \
    && mkdir -p /home/dataiku ${DSS_DATADIR} \
    && chown -Rh dataiku:dataiku /home/dataiku ${DSS_DATADIR}

# System dependencies
# TODO - much could be removed by building externally the required R packages
RUN echo "deb http://cloud.r-project.org/bin/linux/debian jessie-cran3/" \
          >/etc/apt/sources.list.d/cran.list \
    && apt-key adv --keyserver keys.gnupg.net --recv-key 381BA480 \
    && apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get upgrade -y \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y \
        locales \
        acl \
        curl \
        git \
        libexpat1 \
        nginx-full \
        unzip \
        zip \
        default-jre-headless \
        python2.7 \
        libpython2.7 \
        libfreetype6 \
        libgfortran3 \
        libgomp1 \
        r-base-dev \
        libicu-dev \
        libcurl4-openssl-dev \
        libssl-dev \
        libzmq3-dev \
        pkg-config \
    && rm -rf /var/lib/apt/lists/* \
    && localedef -f UTF-8 -i en_US en_US.UTF-8

# Download and extract DSS kit
RUN DSSKIT="dataiku-dss-$DSS_VERSION" \
    && cd /home/dataiku \
    && echo "+ Downloading kit" \
    && curl -OsS "http://downloads.dataiku.com/public/studio/$DSS_VERSION/$DSSKIT.tar.gz" \
    && echo "+ Extracting kit" \
    && tar xf "$DSSKIT.tar.gz" \
    && rm "$DSSKIT.tar.gz" \
    && echo "+ Compiling Python code" \
    && python2.7 -O -m compileall -q "$DSSKIT"/python "$DSSKIT"/dku-jupyter "$DSSKIT"/python.packages \
    && chown -Rh dataiku:dataiku "$DSSKIT"

# Install required R packages
# TEMPORARY 09-mar-2017 - 0.5.2 is buggy, switch to 0.5.3 which is not on CRAN yet
#RUN R --slave --no-restore \
#    -e "install.packages(c('httr', 'RJSONIO', 'dplyr', 'IRkernel', 'sparklyr', 'ggplot2', 'tidyr'), \
#                        repos=c('file:///home/dataiku/dataiku-dss-$DSS_VERSION/dku-jupyter/R', \
#                                'http://cloud.r-project.org'))"
RUN R --slave --no-restore \
    -e "install.packages(c('httr', 'RJSONIO', 'dplyr', 'IRkernel', 'ggplot2', 'tidyr'), \
                        repos=c('file:///home/dataiku/dataiku-dss-$DSS_VERSION/dku-jupyter/R', \
                                'http://cloud.r-project.org'))" && \
    R --slave --no-restore \
    -e "install.packages(c('methods', 'lazyeval', 'dplyr', 'DBI', \
                           'readr', 'digest', 'config', 'rappdirs', 'assertthat', \
                           'rprojroot', 'withr', 'httr', 'jsonlite', 'base64enc'), \
                         repos='http://cloud.r-project.org')" && \
    curl -OL https://github.com/rstudio/sparklyr/releases/download/v0.5.3/sparklyr_0.5.3.tar.gz && \
    R CMD INSTALL sparklyr_0.5.3.tar.gz && \
    rm sparklyr_0.5.3.tar.gz


# Entry point
WORKDIR /home/dataiku
USER dataiku

COPY run.sh /home/dataiku/

EXPOSE $DSS_PORT

CMD [ "/home/dataiku/run.sh" ]
