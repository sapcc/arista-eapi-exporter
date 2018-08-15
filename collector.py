from prometheus_client.core import GaugeMetricFamily

import pyeapi
import ssl
import socket
import logging
import os
import errno

class AristaMetricsCollector(object):
    def __init__(self, config, hostname, exclude=list):
        self._exclude = exclude
        self._username = os.environ['ARISTA_USERNAME'] or config['username']
        self._password = os.environ['ARISTA_PASSWORD'] or config['password']
        self._protocol = config['protocol']
        self._timeout = config['timeout']
        self._hostname = hostname
        self._labels = {}
        self._get_labels()
        self._job = config['job']

    def connect_switch(self, command):
        # switch off certificate validation
        ssl._create_default_https_context = ssl._create_unverified_context

        switch_result = ""

        # set the default timeout 
        logging.debug("setting timeout to %s", self._timeout)

        connection = pyeapi.connect(transport=self._protocol, host=self._hostname, username=self._username, password=self._password, timeout=self._timeout)
        logging.info("Connecting to switch %s", self._hostname)
        try:
            logging.debug("Running command %s", command) 
            switch_result = connection.execute([command])
        except socket.timeout as excptn:
            logging.error("ERROR: %s", excptn)
        finally:
            if switch_result == "":
                logging.warn("No result from switch %s", self._hostname)
            return switch_result
    
    def _get_labels(self):
        # Get the switch info for the labels
        switch_info = self.connect_switch (command="show version")
        if switch_info:
            labels_switch = {'job': self._job, 'instance': self._hostname, 'model': switch_info['result'][0]['modelName'], 'serial': switch_info['result'][0]['serialNumber'], 'mac': switch_info['result'][0]['systemMacAddress']}
            self._labels.update(labels_switch)

    def collect(self):
        if self._labels:

            # Get the tcam usage data
            switch_tcam = self.connect_switch (command="show hardware capacity")

            if switch_tcam:
                metrics = GaugeMetricFamily('switch_usage','Arista Switch TCAM Usage',labels=self._labels)
                for entry in switch_tcam['result'][0]['tables']:
                    # add the chip and feature names as labels to the switch info labels
                    labels = {}
                    labels = ({'chip':entry["chip"], 'feature':entry["feature"]})
                    if entry['table'] not in self._exclude:
                        logging.debug("Adding: table=%s value=%s labels=%s", entry['table'], entry["usedPercent"], labels)
                        labels.update(self._labels)
                        metrics.add_sample(entry['table'], value=entry["usedPercent"], labels=labels)
                    else:
                        logging.debug("Excluding: table=%s value=%s labels=%s", entry['table'], entry["usedPercent"], labels)

                yield metrics

            else:
                pass
        else:
            pass
