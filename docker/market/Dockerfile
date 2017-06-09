FROM ubuntu:16.04
MAINTAINER plebnet

WORKDIR /root

# This dockerfile starts tribler including market for use by plebnet

RUN apt update && apt install -y \
# General dependencies
	git \
# Tribler (headless) dependencies
	python-twisted \
	python-libtorrent \
	python-apsw \
	python-chardet \
	python-cherrypy3 \
	python-nacl \
	python-m2crypto \
	python-configobj \
	python-netifaces \
	python-leveldb \
	python-decorator \
	python-feedparser \
# Market community dependencies
	python-keyring \
	python-libnacl \
	python-ecdsa \
	python-pbkdf2 \
	python-requests \
	python-protobuf \
	python-socks \
	python-dnspython \
	python-jsonrpclib \
	python-keyrings.alt \
# Market community reputation dependencies
	python-networkx \
	python-scipy
	
ADD https://pypi.python.org/packages/63/31/6768a72cdca5dbd299ae798b690801e6c9c2f018332eec3c5fca79370dba/pyaes-1.6.0.tar.gz .
RUN tar -xvzf pyaes-1.6.0.tar.gz
WORKDIR pyaes-1.6.0
RUN python setup.py install

WORKDIR /root

# Install tribler
RUN git clone --recursive https://github.com/devos50/tribler
WORKDIR tribler
RUN git checkout market_community
RUN git submodule update --init --recursive electrum

# Download dispersy
WORKDIR Tribler
RUN git submodule update --init --recursive dispersy

# Open up RESTapi port to host system
WORKDIR /root/tribler
RUN sed -ie 's/"127.0.0.1"/"0.0.0.0"/g' /root/tribler/Tribler/Core/Modules/restapi/rest_manager.py

# Copy plebnet twisted plugin for tribler market
COPY ./twistd_plugin/plebnet_plugin.py /root/tribler/twisted/plugins/

# Start tribler at port 8085
# DO NOT bind this port to anything else than the host machine
WORKDIR /root/tribler
CMD twistd -n plebnet -p 8085
