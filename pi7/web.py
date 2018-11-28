import logging
import requests
import uuid
import json

from flask         import request, render_template, send_from_directory
from flask_restful import Resource

from pi7    import server, api
from pi7.mq import broker

@server.route("/")
@server.route("/<string:page>.html")
def render_home(page="home"):
  return render_template(page + ".html")

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
    broker.publish("salesorder/request", json.dumps(event))

api.add_resource(
  WebSalesOrderRequest,
  "/api/web/salesorder/request"
)
