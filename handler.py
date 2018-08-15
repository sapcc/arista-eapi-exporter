import falcon
import logging
import socket

from wsgiref import simple_server
from prometheus_client.exposition import CONTENT_TYPE_LATEST
from prometheus_client.exposition import generate_latest

from collector import AristaMetricsCollector

class metricHandler:
    def __init__(self, config, exclude=list):
        self._exclude = exclude
        self._config = config

    def on_get(self, req, resp):

        self._hostname = req.get_param("hostname")

        resp.set_header('Content-Type', CONTENT_TYPE_LATEST)
        if not self._hostname:
            msg = "No hostname provided!"
            logging.error(msg)
            resp.status = falcon.HTTP_400
            resp.body = msg

        try:
            socket.gethostbyname(self._hostname)
        except socket.gaierror as excptn:
            msg = "Hostname does not exist in DNS: {0}".format(excptn)
            logging.error(msg)
            resp.status = falcon.HTTP_400
            resp.body = msg

        else:
            registry = AristaMetricsCollector(
                self._config,
                exclude=self._exclude,
                hostname=self._hostname
                )

            collected_metric = generate_latest(registry)
            resp.body = collected_metric