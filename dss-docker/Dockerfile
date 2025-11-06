FROM almalinux:9

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
    && dnf -y module switch-to nodejs:22 \
    && dnf -y install --enablerepo=crb \
        diffutils \
        file \
        acl \
        dejavu-sans-fonts \
        google-noto-sans-cjk-ttc-fonts \
        google-noto-serif-cjk-ttc-fonts \
        google-noto-sans-thai-fonts \
        google-noto-serif-thai-fonts \
        expat \
        freetype \
        fontconfig \
        git \
        glibc-langpack-en \
        nginx \
        unzip \
        zip \
        procps-ng \
        java-17-openjdk-headless \
        python3 \
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
        libreoffice-writer \
        libreoffice-impress \
        libreoffice-calc \
        python3-devel \
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
    && (cd "$DSSKIT"/resources/graphics-export && npm install puppeteer@24.8.2 fs)

# Entry point
COPY run.sh /home/dataiku/

EXPOSE $DSS_PORT

CMD [ "/home/dataiku/run.sh" ]
