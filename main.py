#import click
from handler import metricHandler
import argparse
from yamlconfig import YamlConfig
import logging
import sys
import falcon
from wsgiref import simple_server
import socket
import os


def falcon_app(port=9200, addr='0.0.0.0', exclude=list):
    logging.info("Starting Arista eAPI Prometheus Server on Port %s", port)
    ip = socket.gethostbyname(socket.gethostname())
    logging.info("Listening on IP %s", ip)
    api = falcon.API()
    api.add_route(
        '/arista',
        metricHandler(exclude=exclude, config=config)
    )

    try:
        httpd = simple_server.make_server(addr, port, api)
    except Exception as e:
        logging.error("Couldn't start Server:" + str(e))

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()
        logging.info("Stopping Arista eAPI Prometheus Server")

def enable_logging():
    # enable logging
    logger = logging.getLogger()
    app_environment = os.getenv('APP_ENV', default="production").lower()
    if app_environment == "production":
        logger.setLevel('INFO')
    else:
        logger.setLevel('DEBUG')
    format = '%(asctime)-15s %(process)d %(levelname)s %(filename)s:%(lineno)d %(message)s'
    logging.basicConfig(stream=sys.stdout, format=format)

if __name__ == '__main__':
    # command line options
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--config", help="Specify config yaml file", metavar="FILE", required=False, default="config.yml")
    args = parser.parse_args()

    # get the config
    config = YamlConfig(args.config)

    enable_logging()

    falcon_app(port=config['listen_port'], exclude=config['exclude'])
