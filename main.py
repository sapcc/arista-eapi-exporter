#import click
from handler import metricHandler
import argparse
from yamlconfig import YamlConfig
import logging
import sys
import falcon
from wsgiref import simple_server
import socket


def falcon_app(port=9200, addr='0.0.0.0', exclude=list):
    logger.info("Starting Arista eAPI Prometheus Server on Port %s", port)
    ip = socket.gethostbyname(socket.gethostname())
    logger.info("Listening on IP %s", ip)
    api = falcon.API()
    api.add_route(
        '/arista',
        metricHandler(exclude=exclude, config=config)
    )

    try:
        httpd = simple_server.make_server(addr, port, api)
    except Exception as e:
        logger.error("Couldn't start Server:" + str(e))

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()
        logger.info("Stopping Arista eAPI Prometheus Server")

    
if __name__ == '__main__':
    # command line options
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--config", help="Specify config yaml file", metavar="FILE", required=False, default="config.yml")
    args = parser.parse_args()

    # get the config
    config = YamlConfig(args.config)

    # enable logging
    logger = logging.getLogger()
    if config['loglevel']:
        logger.setLevel(logging.getLevelName(config['loglevel'].upper()))
    else:
        logger.setLevel('INFO')
    format = '%(asctime)-15s %(process)d %(levelname)s %(filename)s:%(lineno)d %(message)s'
    logging.basicConfig(stream=sys.stdout, format=format)

    falcon_app(port=config['listen_port'], exclude=config['exclude'])
