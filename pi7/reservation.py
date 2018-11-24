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
  def __init__(self, guid=None):
    self.guid       = guid or str(uuid.uuid4())
    self.processId   = None
    self.reservation = None

  def in_context_of(self, processId):
    self.processId = processId
    return self

  def make(self, reservation):
    logging.info(
      "reservation: making reservation for {0}".format(reservation["reserved"])
    )
    self.reservation = reservation
    self.update_historic({"status" : "unconfirmed"})

  def persist(self):
    db.reservation.update_one(
      { "_id": self.guid },
      { "$set" : {
        "processId"   : self.processId,
        "reservation" : self.reservation
      }}, upsert=True)
    logging.info("reservation: persisted {0}".format(self.guid))
    return self

  def load(self):
    data = db.reservation.find_one({ "_id" : self.guid })
    if data:
      self.processId   = data["processId"]
      self.reservation = data["reservation"]
    return self

  def confirm(self):
    logging.info("reservation: confirming {0}".format(guid))
    self.update_historic({ "status" : "confirmed" })
    reservation = self.reservation
    reservation["_id"] = self.guid
    reservation.pop("history")
    requests.post(
      url("/api/integration/confirm/reservation"),
      json={
        "processId"   : self.processId,
        "reservation" : reservation
      })

  def update_historic(self, update):
    if not "history" in self.reservation:
      self.reservation["history"] = []
    for key in update:
      self.reservation[key] = update[key]
    update["time"] = int(time.time())
    self.reservation["history"].append(update)
    self.persist()

# REST API

class ReservationStore(Resource):
  def get(self, status):
    return [ x for x in db.reservation.find({"reservation.status": status}) ]
  def post(self, status):
    guid = request.get_json()
    Reservation(guid).load().confirm()

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
      Reservation().in_context_of(event["processId"]).make(reservation)

api.add_resource(
  ReservationSalesOrderRequest,
  "/api/reservation/request/salesorder"
)
