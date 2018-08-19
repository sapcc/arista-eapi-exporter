# arista-eapi-exporter

This is a Prometheus Exporter for extracting metrics from a Arista Switch using the Arista's eAPI and the Python Client for eAPI [pyeapi](https://pypi.org/project/pyeapi/).

The current implementation retrieves the memory usage data via `show hardware capacity`command and returns the table rows as a Gauge metric using some of the switches information as labels like the serial, the model, the mac address and the hostname.

Future implementations could easily also gather other data from the switches.

The hostname of the switch has to be passed as **target parameter** in the http call.

## Prerequisites and Installation

The exporter was written for Python 3.6 or newer. To install all modules needed you have to run the following command:

```bash
pip3 install --no-cache-dir -r requirements.txt
```

There is also a docker file available to create a docker container to run the exporter.

## The config.yml file

* The **listen_port** is providing the port on which the exporter is waiting to receive calls.

* The credentials for login to the switches can either be added to the config.yaml file or passed via environment variables ARISTA_USERNAME and ARISTA_PASSWORD. The environment overwrites the settings in the config file

* The logging level can be specified in the config file or overwritten via environment variable

* The **timeout** parameter specifies the amount of time to wait for an answer from the switch.

* With the **exclude** parameter you can filter the output of the exporter. In following example some of the tables are excluded.

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