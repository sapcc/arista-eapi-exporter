# arista-eapi-exporter

This is a Prometheus Exporter for extracting metrics from an Arista Switch using the Arista's eAPI and the Python Client for eAPI [pyeapi](https://pypi.org/project/pyeapi/).

The current implementation retrieves the memory usage data via `show hardware capacity` command and returns the table rows as a Gauge metric using some of the switches information as labels like the serial, the model, the firmware version and the hostname (arista_tcam).
It also returns a metric (arista_up) indicating if the switch was reachable or not and one returning the response time of the show version call (arista_response).

Future implementations could easily also gather other data from the switches.

The hostname of the switch has to be passed as **target parameter** in the http call.

## Example Call

if you are logged in to the POD running the exporter you can call

```
curl http://localhost:9200/arista?target=eu-de-1-asw202-bm001.cc.eu-de-1.cloud.sap
```

## Prerequisites and Installation

The exporter was written for Python 3.6 or newer. To install all modules needed you have to run the following command:

```bash
pip3 install --no-cache-dir -r requirements.txt
```

There is also a docker file available to create a docker container to run the exporter.

## The config.yml file

* The **listen_port** is providing the port on which the exporter is waiting to receive calls.

* The credentials for login to the switches can either be added to the config.yaml file or passed via environment variables `ARISTA_USERNAME` and `ARISTA_PASSWORD`. The environment overwrites the settings in the config file.

* The **loglevel** can be specified in the config file. If omitted the default level is `INFO`.

* The **timeout** parameter specifies the amount of time to wait for an answer from the switch. It can be defined in config.yaml ir passed via environment variable `TIMEOUT`. The environment overwrites the settings in the config file.

* With the **exclude** parameter you can filter the output of the exporter. In the following example some of the tables are excluded.

* The **job** parameter specifies the Prometheus job that will be passed as label.

### Example of a config file

```text
listen_port: 9200
username: <your username>
password: <your password>
loglevel: <INFO|DEBUG>
timeout: 20
exclude: ['NextHop', 'LPM', 'Host', 'MAC', 'VFP']
job: arista
```
