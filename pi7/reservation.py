import logging
import requests
import time

from flask         import request
from flask_restful import Resource

from pi7             import server, api
from pi7.integration import url

class Reservation(object):
  def __init__(self):
    self.processId   = None
    self.reservation = None

  def in_context_of(self, processId):
    self.processId = processId
    return self

  def make(self, reservation):
    logging.info(
      "reservation: making reservation for {0}".format(reservation["reserved"])
    )
    time.sleep(1) # simulate some work that must be done
    self.reservation = reservation
    self.confirm()
  
  def confirm(self):
    logging.info("reservation: confirming")
    self.reservation["status"] = "confirmed"
    requests.post(
      url("/api/integration/confirm/reservation"),
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
      Reservation().in_context_of(event["processId"]).make(reservation)

api.add_resource(
  ReservationSalesOrderRequest,
  "/api/reservation/request/salesorder"
)
