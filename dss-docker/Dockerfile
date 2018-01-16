FROM dataiku/dss:4.1.0

# Entry point
WORKDIR /home/dataiku

EXPOSE $DSS_PORT

USER root

ADD http://archive.apache.org/dist/hadoop/core/hadoop-2.8.3/hadoop-2.8.3.tar.gz /home/dataiku/

ADD conf/ /home/dataiku/hadoop-2.8.3/conf

COPY run-with-hadoop.sh /home/dataiku/

ADD hadoop /usr/bin/

ADD http://www-eu.apache.org/dist/spark/spark-2.2.0/spark-2.2.0-bin-hadoop2.7.tgz /home/dataiku/

ADD spark-env.sh /home/dataiku/spark-2.2.0-bin-hadoop2.7/conf/

ADD spark-submit /usr/bin/

RUN chown dataiku:dataiku /usr/bin/hadoop \
	&& chown dataiku:dataiku /usr/bin/spark-submit \
	&& chown -R dataiku:dataiku /home/dataiku/spark-2.2.0-bin-hadoop2.7/ \
	&& chown -R dataiku:dataiku /home/dataiku/hadoop-2.8.3/

CMD [ "/home/dataiku/run-with-hadoop.sh" ]