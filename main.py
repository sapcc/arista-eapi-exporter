from handler import metricHandler
from handler import welcomePage
import argparse
import yaml
from wsgiref.simple_server import make_server, WSGIServer, WSGIRequestHandler
import logging
import sys
import falcon
from wsgiref import simple_server
import socket
import threading
from socketserver import ThreadingMixIn
import os

class _SilentHandler(WSGIRequestHandler):
    """WSGI handler that does not log requests."""

    def log_message(self, format, *args):
        """Log nothing."""
        pass

class ThreadingWSGIServer(ThreadingMixIn, WSGIServer):
    """Thread per request HTTP server."""
    pass

def falcon_app():
    port = int(os.getenv('LISTEN_PORT', config['listen_port']))
    exclude = config['exclude']
    addr = '0.0.0.0'
    logging.info("Starting Arista eAPI Prometheus Server on Port %s", port)

    api = falcon.App()
    api.add_route('/arista', metricHandler(exclude=exclude, config=config))
    api.add_route('/', welcomePage())


    with make_server(addr, port, api, ThreadingWSGIServer, handler_class=_SilentHandler) as httpd:
        httpd.daemon = True
        try:
            httpd.serve_forever()
        except (KeyboardInterrupt, SystemExit):
            logging.info("Stopping Redfish Prometheus Server")

def enable_logging(debug):
    # enable logging
    logger = logging.getLogger()
    app_environment = os.getenv('APP_ENV', default="production").lower()

    if debug or app_environment != "production":
        logger.setLevel('DEBUG')
    else:
        logger.setLevel('INFO')

    format = '%(asctime)-15s %(process)d %(levelname)s %(filename)s:%(lineno)d %(message)s'
    logging.basicConfig(stream=sys.stdout, format=format)

if __name__ == '__main__':
    # command line options
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c",
        "--config",
        help="Specify config yaml file",
        metavar="FILE",
        required=False,
        default="config.yml"
    )
    parser.add_argument(
        "-d", "--debug", 
        help="Debugging mode", 
        action="store_true", 
        required=False
    )
    args = parser.parse_args()

    # get the config
    if args.config:
        try:
            with open(args.config, "r") as config_file:
                config = yaml.load(config_file.read(), Loader=yaml.FullLoader)
        except FileNotFoundError as err:
            print(f"Config File not found: {err}")
            exit(1)

    enable_logging(args.debug)

    falcon_app()
