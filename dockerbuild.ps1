$version = "v0.3.1"

docker build . -t keppel.eu-de-1.cloud.sap/ccloud/arista-exporter:$version
docker login keppel.eu-de-1.cloud.sap
docker push keppel.eu-de-1.cloud.sap/ccloud/arista-exporter:$version
