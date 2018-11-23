import logging
import requests
import uuid
import json

from flask         import request, render_template
from flask_restful import Resource

from pi7             import server, api
from pi7.integration import url

@server.route("/")
def render_home():
  return render_template("home.html")

class WebSalesOrderRequest(Resource):
  def post(self):
    salesorder = json.loads(request.get_json())
    logging.info("web: received sales order request")
    event = {
      "processId"  : str(uuid.uuid4()),
      "salesorder" : salesorder
    }
    logging.info("     assigned processId {0}".format(event["processId"]))
    logging.info("     publishing sales order request event")
    requests.post(url("/api/integration/request/salesorder"), json=event)

api.add_resource(
  WebSalesOrderRequest,
  "/api/web/salesorder/request"
)

@server.route("/store")
def render_store():
  return render_template("store.html")
