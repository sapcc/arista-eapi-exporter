FROM docker.io/ubuntu:18.04

RUN export DEBIAN_FRONTEND=noninteractive \
    && apt-get update \
    && apt-get install -y python3 \
    && apt-get install -y python3-pip

RUN mkdir /arista_exporter

WORKDIR /arista_exporter

COPY requirements.txt /arista_exporter
RUN pip3 install --no-cache-dir -r requirements.txt

COPY *.py /arista_exporter/
COPY config.yml /arista_exporter/

ENTRYPOINT [ "python3", "-u", "./main.py"]