FROM ubuntu:24.04

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update \
 && apt-get -y install \
    blender \
    python3 \
    python3-pip \
 && rm -rf /var/cache/apt/*

COPY docker/3d_mask_convert/requirements.txt /opt
# imagecodecs' setup.py seems to import numpy
# --break-system-packages since we need to install into the same environment
# that Blender uses for its Python scripting
RUN python3 -m pip install --break-system-packages numpy \
 && python3 -m pip install --break-system-packages -r /opt/requirements.txt \
 && rm -rf /root/.cache/pip /opt/requirements.txt

COPY bin/common /opt
COPY bin/3d_mask_convert /opt
