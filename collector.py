from prometheus_client.core import GaugeMetricFamily

import pyeapi
import ssl
import socket
import logging
import os
import json
import time
import re

class AristaMetricsCollector(object):
    def __init__(self, config, target, exclude=list):
        self._exclude = exclude
        self._username = os.getenv('ARISTA_USERNAME',config['username'])
        self._password = os.getenv('ARISTA_PASSWORD',config['password'])
        self._protocol = config['protocol'] or "https"
        self._timeout = int(os.getenv('TIMEOUT', config['timeout']))
        self._job = config['job']
        self._target = target
        self._connection = False
        self._labels = {}
        self._switch_up = 0
        self._responstime = 0
        self._memtotal = 0
        self._memfree = 0
        self._get_labels()


    def get_connection(self):
        # switch off certificate validation
        ssl._create_default_https_context = ssl._create_unverified_context
        # set the default timeout
        logging.debug(f"Setting timeout to {self._timeout}")
        if not self._connection:
            logging.info(f"Connecting to switch {self._target}")
            self._connection = pyeapi.connect(
                transport=self._protocol,
                host=self._target,
                username=self._username,
                password=self._password,
                timeout=self._timeout,
            )
            # workaround to allow sslv3 ciphers for python =>3.10
            self._connection.transport._context.set_ciphers('DEFAULT')
        return self._connection
    
    def connect_switch(self, command):

        switch_result = ""

        connection = self.get_connection()

        data = {
            "jsonrpc": "2.0",
            "method": "runCmds",
            "params": {
                "format": "json",
                "timestamps": "true",
                "autoComplete": "false",
                "expandAliases": "false",
                "cmds": [command],
                "version": 1
            },
            "id": "EapiExplorer-1"
        }

        try:
            logging.debug(f"{self._target}: Running command {command}") 
            switch_result = connection.execute([command])

        except (pyeapi.eapilib.ConnectionError, socket.timeout) as pyeapi_connect_except:
            logging.error(f"{self._target}: PYEAPI Client Connection Exception: {pyeapi_connect_except}")

        except pyeapi.eapilib.CommandError as pyeapi_command_except:
            logging.error(f"{self._target}: PYEAPI Client Command Exception: {pyeapi_command_except}")

        finally:
            return switch_result
    
    def _get_labels(self):
        model   = "unknown"
        serial  = "unknown"
        version = "unknown"

        start = time.time()
        # Get the switch info for the labels
        switch_info = self.connect_switch (command="show version")

        if switch_info:
            logging.debug(f"{self._target}: Received a result from switch")
            model = switch_info['result'][0]['modelName']
            serial = switch_info['result'][0]['serialNumber']
            version = switch_info['result'][0]['version']
            self._switch_up = 1

        else:
            logging.debug(f"{self._target}: No result received from switch")
            self._switch_up = 0

        labels_switch = {'job': self._job, 'instance': self._target, 'model': model, 'serial': serial, 'version': version}

        end = time.time()
        self._responstime = end - start
        self._labels.update(labels_switch)

    def collect(self):

        # Export the up and response metrics
        info_metrics = GaugeMetricFamily('arista_monitoring_info','Arista Switch Monitoring',labels=self._labels)
        info_metrics.add_sample('arista_up', value=self._switch_up, labels=self._labels)
        info_metrics.add_sample('arista_response', value=self._responstime, labels=self._labels)
        
        yield info_metrics

        if self._switch_up == 1:

            logging.debug(f"{self._target}: Switch is rechable.")
            # Export the memory usage data
            mem_metrics = GaugeMetricFamily('switch_monitoring_memdata','Arista Switch Monitoring Memory Usage Data',labels=self._labels)
            mem_metrics.add_sample('arista_mem_total', value=self._memtotal, labels=self._labels)
            mem_metrics.add_sample('arista_mem_free', value=self._memfree, labels=self._labels)
            logging.debug(f"Exporting metrics arista_mem_total={self._memtotal}")
            logging.debug(f"Exporting metrics arista_mem_free={self._memfree}")
            yield mem_metrics

            # Get the tcam usage data
            switch_tcam = self.connect_switch (command="show hardware capacity")

            if switch_tcam:
                tcam_metrics = GaugeMetricFamily('switch_monitoring_data','Arista Switch Monitoring TCAM Usage Data',labels=self._labels)
                for entry in switch_tcam['result'][0]['tables']:
                    # add the chip and feature names as labels to the switch info labels
                    labels = {}
                    labels = ({'table': entry['table'], 'chip':entry["chip"], 'feature':entry["feature"]})
                    if entry['table'] not in self._exclude:
                        labels.update(self._labels)
                        tcam_metrics.add_sample('arista_tcam', value=entry["usedPercent"], labels=labels)
                    else:
                        logging.debug(f"{self._target}: Excluding: table={entry['table']} value={entry['usedPercent']} labels={labels}")

                yield tcam_metrics
            
            else:
                pass

            switch_port_stats = self.connect_switch(command="show interfaces counters rates")
            regex_pattern = re.compile('.*reserved.*', re.IGNORECASE)

            if switch_port_stats:
                port_stats_metrics = GaugeMetricFamily('switch_monitoring_ports','Arista Switch Monitoring Port Statistics',labels=self._labels)
                for port_entry in switch_port_stats['result'][0]['interfaces']:
                    port_values = switch_port_stats['result'][0]['interfaces'][port_entry]
                    port_description = port_values['description'].replace("-> ","")
                    for port_value in port_values:
                        if port_value != "description" and port_value != 'interval' and not regex_pattern.match(port_description):
                            labels = {}
                            labels = ({'port': port_entry, 'stat': port_value, 'description': port_description})
                            labels.update(self._labels)
                            port_stats_metrics.add_sample('arista_port_stats', value=float(port_values[port_value]), labels=labels)

                yield port_stats_metrics
