FROM hubmap/segmentations:1.2.4

COPY docker/segmentation/requirements.txt /opt
RUN pip3 install -r /opt/requirements.txt \
 && rm -rf /root/.cache/pip /opt/requirements.txt

COPY CellSegmentationEvaluator /opt/CellSegmentationEvaluator
RUN cd /opt/CellSegmentationEvaluator/pip_package \
 && pip install . \
 && cd /opt \
 && rm -rf /opt/CellSegmentationEvaluator

COPY 3DCellComposer /opt

COPY bin/common /opt
COPY data /data

WORKDIR /opt
