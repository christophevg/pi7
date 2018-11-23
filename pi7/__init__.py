import os
import logging
import json

from flask import Flask, make_response
import flask_restful

# setup clean console logger
logger = logging.getLogger()

formatter = logging.Formatter(
  "[%(asctime)s] [%(process)d] [%(levelname)s] %(message)s",
  "%Y-%m-%d %H:%M:%S %z"
)

if len(logger.handlers) > 0:
  logger.handlers[0].setFormatter(formatter)
else:
  consoleHandler = logging.StreamHandler()
  consoleHandler.setFormatter(formatter)
  logger.addHandler(consoleHandler)

LOG_LEVEL = os.environ.get("LOG_LEVEL") or "DEBUG"
logger.setLevel(logging.getLevelName(LOG_LEVEL))

# silence requests logger a bit

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

# setup server and REST API
server = Flask(__name__)

def output_json(data, code, headers={}):
  resp = make_response(json.dumps(data), code)
  resp.headers.extend(headers)
  return resp

api = flask_restful.Api(server)
api.representations = { 'application/json': output_json }

import pi7.web
import pi7.integration
import pi7.reservation
import pi7.salesorder
