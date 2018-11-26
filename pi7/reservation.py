import logging
import requests
import time
import uuid

from flask         import request
from flask_restful import Resource

from pi7             import server, api
from pi7.store       import Storable, historic
from pi7.integration import url

@historic
class Reservation(Storable):
  def on_initial_history(self):
    self.log("making reservation for {0}".format(self["reserved"]))
    self.update_historic({"status" : "unconfirmed"})

  def confirm(self):
    self.log("confirming {0}".format(self.guid))
    self.update_historic({ "status" : "confirmed" })
    requests.post(
      url("/api/integration/confirm/reservation"),
      json={
        "processId"   : self.processId,
        "reservation" : self.marshall(external=True)
      })

# REST API

class ReservationStore(Resource):
  def get(self, status):
    return [ x for x in Reservation.collection().find({"object.status": status}) ]
  def post(self, status):
    guid = request.get_json()
    Reservation(guid).confirm()

api.add_resource(
  ReservationStore,
  "/api/store/reservation/<string:status>"
)

# event consumer

class ReservationSalesOrderRequest(Resource):
  def post(self):
    event = request.get_json()
    logging.info("reservation: received sales order request")
    for reservation in event["salesorder"]["reservations"]:
      Reservation().in_context_of(event["processId"], load=False).make(reservation)

api.add_resource(
  ReservationSalesOrderRequest,
  "/api/reservation/request/salesorder"
)
