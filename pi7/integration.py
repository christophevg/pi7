import logging
import requests

from flask         import request
from flask_restful import Resource

from pi7 import server, api

HOST = os.environ.get("INTEGRATION_URL", "http://localhost:8000")

def url(path):
  return HOST + "/" + path

# integration platform event processors

class IntegrationSalesOrderRequest(Resource):
  def post(self):
    data = request.get_json()
    logging.info("integration: received sales order request")
    logging.info("             delivering to sales order and reservation components")
    requests.post(url("/api/salesorder/request/salesorder"), json=data)
    requests.post(url("/api/reservation/request/salesorder"), json=data)

api.add_resource(
  IntegrationSalesOrderRequest,
  "/api/integration/request/salesorder"
)

class IntegrationReservationConfirmed(Resource):
  def post(self):
    data = request.get_json()
    logging.info("integration: received reservation confirmation")
    logging.info("             delivering to sales order component")
    requests.post(url("/api/salesorder/confirm/reservation"), json=data)

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
