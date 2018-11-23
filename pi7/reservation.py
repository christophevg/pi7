import logging
import requests
import time
import uuid

from flask         import request
from flask_restful import Resource

from pi7             import server, api
from pi7.store       import db
from pi7.integration import url

class Reservation(object):
  def __init__(self):
    self.guid       = str(uuid.uuid4())
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
    self.persist()
    self.confirm()
  
  def persist(self):
    db.reservation.update_one(
      { "_id": self.guid },
      { "$set" : {
        "processId"   : self.processId,
        "reservation" : self.reservation
      }}, upsert=True)
    logging.info("reservation: persisted {0}".format(self.guid))
    return self
  
  def confirm(self):
    logging.info("reservation: confirming")
    self.reservation["status"] = "confirmed"
    self.persist()
    reservation = self.reservation
    reservation["_id"] = self.guid
    requests.post(
      url("/api/integration/confirm/reservation"),
      json={
        "processId"   : self.processId,
        "reservation" : reservation
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
