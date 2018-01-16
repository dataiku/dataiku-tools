#!/bin/bash -e

DSS_INSTALLDIR="/home/dataiku/dataiku-dss-$DSS_VERSION"
export SPARK_HOME="/home/dataiku/spark-2.2.0-bin-hadoop2.7"

if [ ! -f "$DSS_DATADIR"/bin/env-default.sh ]; then
	chown dataiku:dataiku "$DSS_DATADIR"
	# Initialize new data directory
	su dataiku -c "$DSS_INSTALLDIR/installer.sh -d $DSS_DATADIR -p $DSS_PORT"
	su dataiku -c "$DSS_DATADIR/bin/dssadmin install-R-integration"
	su dataiku -c '"$DSS_DATADIR"/bin/dssadmin install-hadoop-integration'
	su dataiku -c '"$DSS_DATADIR"/bin/dssadmin install-spark-integration'
	su dataiku -c 'echo "dku.registration.channel=docker-image" >>"$DSS_DATADIR"/config/dip.properties'

elif [ $(bash -c 'source "$DSS_DATADIR"/bin/env-default.sh && echo "$DKUINSTALLDIR"') != "$DSS_INSTALLDIR" ]; then
	# Upgrade existing data directory.  This is not tested!!
	"$DSS_INSTALLDIR"/installer.sh -d "$DSS_DATADIR" -u -y
	"$DSS_DATADIR"/bin/dssadmin install-R-integration
	"$DSS_DATADIR"/bin/dssadmin install-hadoop-integration
	"$DSS_DATADIR"/bin/dssadmin install-spark-integration

fi

mkdir -p /home/dataiku/dss/lib/jdbc
curl 'https://storage.googleapis.com/jdbc-drivers/sqljdbc42.jar' -o /home/dataiku/dss/lib/jdbc/sqljdbc42.jar
chown dataiku:dataiku /home/dataiku/dss/lib/jdbc
su dataiku -c 'exec "$DSS_DATADIR"/bin/dss run'
