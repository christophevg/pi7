import logging
import requests
import time

from flask         import request
from flask_restful import Resource

from pi7 import server, api

class Reservation(object):
  def __init__(self, origin, processId=None):
    self.origin = origin
    self.processId = processId

  def make(self, reservation):
    self.reservation = reservation
    logging.info(
      "reservation: making reservation for {0}".format(
        reservation["reserved"]
      )
    )
    time.sleep(1) # simulate some work that must be done
    self.confirm()
  
  def confirm(self):
    logging.info("reservation: confirming")
    self.reservation["status"] = "confirmed"
    requests.post(self.origin + "/api/integration/confirm/reservation",
                  json={
                    "processId"   : self.processId,
                    "reservation" : self.reservation
                  })

# event consumer

class ReservationSalesOrderRequest(Resource):
  def post(self):
    event = request.get_json()
    logging.info("reservation: received sales order request")
    for reservation in event["salesorder"]["reservations"]:
      Reservation(
        request.host_url,
        processId=event["processId"]
      ).make(reservation)

api.add_resource(
  ReservationSalesOrderRequest,
  "/api/reservation/request/salesorder"
)
