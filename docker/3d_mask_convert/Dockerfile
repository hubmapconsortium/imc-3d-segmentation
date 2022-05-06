FROM ubuntu:20.04

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update \
 && apt-get -y install \
    blender \
    python3 \
    python3-pip \
 && rm -rf /var/cache/apt/*

COPY docker/3d_mask_convert/requirements.txt /opt
# imagecodecs' setup.py seems to import numpy
RUN python3 -m pip install numpy \
 && python3 -m pip install -r /opt/requirements.txt \
 && rm -rf /root/.cache/pip /opt/requirements.txt

COPY bin/common /opt
COPY bin/3d_mask_convert /opt
