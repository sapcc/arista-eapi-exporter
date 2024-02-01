FROM keppel.eu-de-1.cloud.sap/ccloud-dockerhub-mirror/library/ubuntu:latest

RUN export DEBIAN_FRONTEND=noninteractive \
    && apt update \
    && apt upgrade -y \
    && apt install -y python3.11 \
    && apt install -y python3-pip \
    && apt install -y curl

ARG FOLDERNAME=arista_exporter

RUN mkdir /${FOLDERNAME}

WORKDIR /${FOLDERNAME}

RUN pip3 install --upgrade pip
COPY requirements.txt /${FOLDERNAME}
RUN pip3 install --no-cache-dir -r requirements.txt

COPY *.py /${FOLDERNAME}/
COPY config.yml /${FOLDERNAME}/

ENTRYPOINT [ "python3", "-u", "./main.py"]

LABEL source_repository="https://github.com/sapcc/arista-eapi-exporter"
LABEL maintainer="Bernd Kuespert <bernd.kuespert@sap.com>"
