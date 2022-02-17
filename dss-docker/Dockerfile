FROM almalinux:8

ARG dssVersion

ENV DSS_VERSION="$dssVersion" \
    DSS_DATADIR="/home/dataiku/dss" \
    DSS_PORT=10000

# Dataiku account and data dir setup
RUN useradd dataiku \
    && mkdir -p /home/dataiku ${DSS_DATADIR} \
    && chown -Rh dataiku:dataiku /home/dataiku ${DSS_DATADIR}

# System dependencies
RUN yum install -y \
        epel-release \
    && yum install -y \
        glibc-langpack-en \
        file \
        acl \
        expat \
        git \
        nginx \
        unzip \
        zip \
        ncurses-compat-libs \
        java-1.8.0-openjdk \
        python2 \
        python36 \
        freetype \
        libgfortran \
        libgomp \
        libicu-devel \
        libcurl-devel \
        openssl-devel \
        libxml2-devel \
        npm \
        gtk3 \
        libXScrnSaver \
        alsa-lib \
        libX11-xcb \
        python2-devel \
        python36-devel \
    && yum clean all

# Build R 3.6 from source
COPY build-r36.sh /tmp/
RUN /tmp/build-r36.sh \
    && rm -f /tmp/build-r36.sh

# Download and extract DSS kit
RUN DSSKIT="dataiku-dss-$DSS_VERSION" \
    && cd /home/dataiku \
    && echo "+ Downloading kit" \
    && curl -OsS "https://cdn.downloads.dataiku.com/public/studio/$DSS_VERSION/$DSSKIT.tar.gz" \
    && echo "+ Extracting kit" \
    && tar xf "$DSSKIT.tar.gz" \
    && rm "$DSSKIT.tar.gz" \
    && "$DSSKIT"/scripts/install/installdir-postinstall.sh "$DSSKIT" \
    && (cd "$DSSKIT"/resources/graphics-export && npm install puppeteer@1.20.0 fs) \
    && chown -Rh dataiku:dataiku "$DSSKIT"

# Install required R packages
RUN mkdir -p /usr/local/lib64/R/site-library \
    && R --slave --no-restore \
        -e "install.packages( \
            c('httr', 'RJSONIO', 'dplyr', 'curl', 'IRkernel', 'sparklyr', 'ggplot2', 'gtools', 'tidyr', \
            'rmarkdown', 'base64enc', 'filelock'), \
            '/usr/local/lib64/R/site-library', \
            repos='https://cloud.r-project.org')"

# Entry point
WORKDIR /home/dataiku
USER dataiku

COPY run.sh /home/dataiku/

EXPOSE $DSS_PORT

CMD [ "/home/dataiku/run.sh" ]
