FROM hubmap/segmentations:1.2.4

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update \
 && apt-get -y install \
    git \
 && rm -rf /var/cache/apt/*

COPY docker/segmentation/requirements.txt /opt
RUN pip3 install -r /opt/requirements.txt \
 && rm -rf /root/.cache/pip /opt/requirements.txt

COPY CellSegmentationEvaluator /opt/CellSegmentationEvaluator
RUN cd /opt/CellSegmentationEvaluator/pip_package \
 && pip install . \
 && cd /opt \
 && rm -rf /opt/CellSegmentationEvaluator

COPY 3DCellComposer /opt

WORKDIR /opt

RUN wget https://hubmap-pipeline-assets.s3.amazonaws.com/deepcell-models/MultiplexSegmentation-9.tar.gz \
 && mkdir -p /opt/.keras/models/0_12_9 \
 && cd /opt/.keras/models/0_12_9 \
 && tar -xf /opt/MultiplexSegmentation-9.tar.gz \
 && rm /opt/MultiplexSegmentation-9.tar.gz

COPY bin/common /opt
COPY data /data
