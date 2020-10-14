$version = "v0.2.2"

docker build . -t keppel.eu-de-1.cloud.sap/ccloud/arista-exporter:$version
docker push keppel.eu-de-1.cloud.sap/ccloud/arista-exporter:$version
