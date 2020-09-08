$version = "v0.2.2"

docker build . -t hub.global.cloud.sap/monsoon/arista-exporter:$version
docker push hub.global.cloud.sap/monsoon/arista-exporter:$version

docker build . -t keppel.eu-de-1.cloud.sap/ccloud/arista-exporter:$version
docker push keppel.eu-de-1.cloud.sap/ccloud/arista-exporter:$version
