#!/bin/bash -e
# Install a locally-compiled version of R 3.6 in a CentOS 8 container image

VERSION="3.6.3"
SOURCE="https://cloud.r-project.org/src/base/R-3/R-$VERSION.tar.gz"
MD5="506c9576ba33e1262ad5b5624db9d96a"

TMPDIR="/tmp.build-r36"

yum -y install --enablerepo=powertools \
  @development \
  gcc-gfortran \
  readline-devel \
  zlib-devel \
  bzip2-devel \
  xz-devel \
  pcre2-devel \
  libcurl-devel \
  libpng-devel \
  libjpeg-turbo-devel \
  cairo-devel \
  pango-devel \
  libtiff-devel \
  libicu-devel \
  java-1.8.0-openjdk-devel \
  texlive \
  texinfo

mkdir -p "$TMPDIR"
cd "$TMPDIR"

curl -OsS "$SOURCE"
echo "$MD5 R-$VERSION.tar.gz" | md5sum -c

tar xf R-"$VERSION".tar.gz
cd R-"$VERSION"
./configure --without-x
make -j 2
make install

cd /
rm -rf "$TMPDIR"
yum clean all
