version="v0.3.0"

docker build . -t keppel.eu-de-1.cloud.sap/ccloud/arista-exporter:${version}
docker push keppel.eu-de-1.cloud.sap/ccloud/arista-exporter:${version}
