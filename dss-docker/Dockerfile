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
RUN dnf -y install epel-release \
    && dnf -y update \
    && dnf -y module switch-to nodejs:20 \
    && dnf -y install --enablerepo=powertools \
        glibc-langpack-en \
        file \
        acl \
        expat \
        git \
        nginx \
        unzip \
        zip \
        ncurses-compat-libs \
        java-17-openjdk-headless \
        python39 \
        freetype \
        libgfortran \
        libgomp \
        R-core-devel \
        libicu-devel \
        libcurl-devel \
        openssl-devel \
        libxml2-devel \
        npm \
        gtk3 \
        libXScrnSaver \
        alsa-lib \
        nss \
        mesa-libgbm \
        libX11-xcb \
        python39-devel \
    && dnf clean all

# Install required R packages
RUN mkdir -p /usr/local/lib/R/site-library \
    && R --slave --no-restore \
        -e "install.packages( \
            c('httr', 'RJSONIO', 'dplyr', 'curl', 'IRkernel', 'sparklyr', 'ggplot2', 'gtools', 'tidyr', \
            'rmarkdown', 'base64enc', 'filelock'), \
            '/usr/local/lib/R/site-library', \
            repos='https://cloud.r-project.org')"

WORKDIR /home/dataiku
USER dataiku

# Download and extract DSS kit
RUN DSSKIT="dataiku-dss-$DSS_VERSION" \
    && echo "+ Downloading kit" \
    && curl -OsS "https://cdn.downloads.dataiku.com/public/studio/$DSS_VERSION/$DSSKIT.tar.gz" \
    && echo "+ Extracting kit" \
    && tar xf "$DSSKIT.tar.gz" \
    && rm "$DSSKIT.tar.gz" \
    && "$DSSKIT"/scripts/install/installdir-postinstall.sh "$DSSKIT" \
    && (cd "$DSSKIT"/resources/graphics-export && npm install puppeteer@23.11.1 fs)

# Entry point
COPY run.sh /home/dataiku/

EXPOSE $DSS_PORT

CMD [ "/home/dataiku/run.sh" ]
