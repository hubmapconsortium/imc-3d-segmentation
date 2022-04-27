FROM hubmap/segmentations:1.2.2

COPY requirements.txt /opt
RUN pip3 install -r /opt/requirements.txt \
 && rm -rf /root/.cache/pip /opt/requirements.txt

COPY bin opt

WORKDIR /opt
