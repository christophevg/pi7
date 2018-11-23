import logging
import requests
import uuid

from flask         import request
from flask_restful import Resource

from pi7             import server, api
from pi7.store       import db
from pi7.integration import url

class SalesOrder(object):
  def __init__(self):
    self.guid       = str(uuid.uuid4())
    self.processId  = None
    self.salesorder = { "reservations": [] }

  def in_context_of(self, processId):
    self.processId = processId
    self.load()
    return self

  def load(self):
    data = db.salesorder.find_one({ "processId" : self.processId })
    if data:
      self.guid = data["_id"]
      self.make(data["salesorder"], persist=False)

  def make(self, salesorder, persist=True):
    reservations = []
    for reservation in salesorder["reservations"]:
      for existing in self.salesorder["reservations"]:
        if reservation["id"] == existing["id"]:
          reservation = existing
      if not "status" in reservation: reservation["status"] = "unconfirmed"
      reservations.append(reservation)
    salesorder["reservations"] = reservations
    self.salesorder = salesorder
    if persist: self.persist()
    return self

  def persist(self):
    db.salesorder.update_one(
      { "_id": self.guid },
      { "$set" : {
        "processId"    : self.processId,
        "salesorder"   : self.salesorder
      }}, upsert=True)
    logging.info("sales order: persisted {0}".format(self.guid))
    self.check()
    return self

  def confirm(self, reservation):
    if "customer" in self.salesorder:
      for i in range(len(self.salesorder["reservations"])):
        if reservation["id"] == self.salesorder["reservations"][i]["id"]:
          self.salesorder["reservations"][i] = reservation
    else:
      self.salesorder["reservations"].append(reservation)
    self.persist()

  def check(self):
    if not "customer" in self.salesorder: return
    all_confirmed = True
    for reservation in self.salesorder["reservations"]:
      all_confirmed = all_confirmed and ( reservation["status"] == "confirmed")
    if all_confirmed:
      logging.info("sales order: all reservations are confirmed")
      requests.post(
        url("/api/integration/confirm/salesorder"),
        json={
          "processId"  : self.processId,
          "salesorder" : self.salesorder
        })

# event consumers

class SalesOrderRequest(Resource):
  def post(self):
    event = request.get_json()
    logging.info("sales order: received sales order request")
    SalesOrder().in_context_of(event["processId"]).make(event["salesorder"])

api.add_resource(
  SalesOrderRequest,
  "/api/salesorder/request/salesorder"
)

class SalesOrderReservationConfirmation(Resource):
  def post(self):
    event = request.get_json()
    logging.info("sales order: received reservation confirmation")
    SalesOrder().in_context_of(event["processId"]).confirm(event["reservation"])

api.add_resource(
  SalesOrderReservationConfirmation,
  "/api/salesorder/confirm/reservation"
)
