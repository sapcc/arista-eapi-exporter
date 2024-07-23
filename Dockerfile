FROM keppel.eu-de-1.cloud.sap/ccloud-dockerhub-mirror/library/ubuntu:latest

RUN export DEBIAN_FRONTEND=noninteractive \
    && apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y python3 \
    && apt-get install -y python3-pip \
    && apt-get install -y curl \
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

ARG FOLDERNAME=arista_exporter

RUN mkdir /${FOLDERNAME}

WORKDIR /${FOLDERNAME}

RUN pip3 install --break-system-packages --upgrade pip --ignore-install
COPY requirements.txt /${FOLDERNAME}
RUN pip3 install --break-system-packages --no-cache-dir -r requirements.txt

COPY *.py /${FOLDERNAME}/
COPY config.yml /${FOLDERNAME}/

ENTRYPOINT [ "python3", "-u", "./main.py"]

LABEL source_repository="https://github.com/sapcc/arista-eapi-exporter"
LABEL maintainer="Bernd Kuespert <bernd.kuespert@sap.com>"
