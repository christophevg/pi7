import os
import logging
import requests
import time
from threading import Thread

from flask         import request
from flask_restful import Resource

from pi7 import server, api

HOST = os.environ.get("INTEGRATION_URL", "http://localhost:8000")

def url(path):
  return HOST + "/" + path

queue = []

def deliver(path, data):
  queue.append({
    "path" : path,
    "data" : data
  })

def process():
  while True:
    time.sleep(0.1)
    while len(queue) > 0:
      msg = queue.pop(0)
      requests.post(url(msg["path"]), json=msg["data"])

t = Thread(target=process)
t.setDaemon(True)
t.start()

# integration platform event processors

class IntegrationSalesOrderRequest(Resource):
  def post(self):
    data = request.get_json()
    logging.info("integration: received sales order request")
    logging.info("             delivering to sales order and reservation components")
    deliver("/api/salesorder/request/salesorder",  data)
    deliver("/api/reservation/request/salesorder", data)

api.add_resource(
  IntegrationSalesOrderRequest,
  "/api/integration/request/salesorder"
)

class IntegrationReservationConfirmed(Resource):
  def post(self):
    data = request.get_json()
    logging.info("integration: received reservation confirmation")
    logging.info("             delivering to sales order component")
    deliver("/api/salesorder/confirm/reservation", data)

api.add_resource(
  IntegrationReservationConfirmed,
  "/api/integration/confirm/reservation"
)

class IntegrationSalesOrderConfirmed(Resource):
  def post(self):
    data = request.get_json()
    logging.info("integration: received sales order confirmation")

api.add_resource(
  IntegrationSalesOrderConfirmed,
  "/api/integration/confirm/salesorder"
)
