# arista-eapi-exporter

This is a Prometheus Exporter for extracting metrics from a Arista Switch using the Arista's eAPI and the Python Client for eAPI [pyeapi](https://pypi.org/project/pyeapi/).

The current implementation retrieves the memory usage data via `show hardware capacity`command and returns the table rows as a Gauge metric using some of the switches information as labels like the serial, the model, the mac address and the hostname.

Future implementations could easily also gather other data from the switches.

The credentials for login to the switches can be either be added to the config.yaml file or passed via environment variables ARISTA_USERNAME and ARISTA_PASSWORD.