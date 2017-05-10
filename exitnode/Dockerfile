FROM ubuntu:16.04
MAINTAINER @Pleb_Net

WORKDIR /root

ENV plebnet="/root/plebnet"
ENV tribler="/root/tribler"

# This dockerfile combines all components needed to run plebnet.
# in its best practices https://docs.docker.com/engine/userguide/eng-image/dockerfile_best-practices/#minimize-the-number-of-layers
# it is noted that one should have containers with one concern. 
# Maybe split these concerns later.


# # Comment
# INSTRUCTION arguments

RUN echo 'Seting up Tribler and its dependencies'

RUN apt update && apt install -y \
	# Install general dependencies
    git \
	# Install tribler dependencies
    libsodium18 \
    python-crypto \
    python-cryptography \
    python-decorator \
    python-feedparser \
    python-leveldb \
    python-libtorrent \
    python-m2crypto \
    python-netifaces \
    python-pil \
    python-pyasn1 \
    python-twisted \
    python2.7 \
    python-chardet \
    python-configobj \
	# Install tribler community dependencies
    python-protobuf

# Clone market_community 
RUN git clone https://www.github.com/devos50/tribler

# Copy Tribler configuration




