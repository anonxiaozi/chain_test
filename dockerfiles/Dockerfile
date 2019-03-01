# deploy noded/pbcli
# escape=\

FROM ubuntu:16.04
LABEL noded="yes" cli="yes"

ENV Dir=/root/work/ noded_service_port=3005 noded_rpc_port=40001 cli_rpc_port=60001 cli_http_port=60002 DATADir=/root/.pb_data

EXPOSE $noded_service_port $noded_rpc_port $cli_rpc_port $cli_http_port

USER root:root
SHELL ["/bin/sh", "-c"]

RUN mkdir $Dir
VOLUME ["${DATADir}"]
WORKDIR $Dir

COPY noded pbcli cli startup_noded.sh $Dir
RUN apt-get -y update; \
	apt-get -y install libgmp-dev gcc flex make bison expect; \
	chmod +x $Dir/startup_noded.sh
ADD https://crypto.stanford.edu/pbc/files/pbc-0.5.14.tar.gz /usr/local/src/
RUN tar xf /usr/local/src/pbc-0.5.14.tar.gz -C /usr/local/src && cd /usr/local/src/pbc-0.5.14 && \
	./configure && make && make install && \
	echo "/usr/local/lib" > /etc/ld.so.conf.d/chain_noded.conf && ldconfig && \
	rm -rf /usr/local/src/{pbc-0.5.14.tar.gz,pbc-0.5.14}

ENTRYPOINT ["/root/work/startup_noded.sh"]
CMD ["run"]
