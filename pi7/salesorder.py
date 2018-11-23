import logging
import requests
import uuid

from flask         import request
from flask_restful import Resource

from pi7           import server, api
from pi7.store     import db

class SalesOrder(object):
  def __init__(self, origin=None, processId=None):
    self.guid         = str(uuid.uuid4())
    self.origin       = origin
    self.processId    = processId
    self.salesorder   = { "reservations": [] }
    self.load()

  def load(self):
    data = db.salesorder.find_one({ "processId" : self.processId })
    if data:
      self.guid = data["_id"]
      self.make(data["salesorder"], persist=False)

  def persist(self):
    db.salesorder.update_one(
      { "_id": self.guid },
      { "$set" : {
        "processId"    : self.processId,
        "origin"       : self.origin,
        "salesorder"   : self.salesorder
      }}, upsert=True)
    logging.info("sales order: persisted {0}".format(self.guid))
    self.check()
    return self

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
        self.origin + "/api/integration/confirm/salesorder",
        json={
          "processId"  : self.processId,
          "salesorder" : self.salesorder
        })

# event consumers

class SalesOrderRequest(Resource):
  def post(self):
    event = request.get_json()
    logging.info("sales order: received sales order request")
    order = SalesOrder(request.host_url, processId=event["processId"])
    order.make(event["salesorder"])

api.add_resource(
  SalesOrderRequest,
  "/api/salesorder/request/salesorder"
)

class SalesOrderReservationConfirmation(Resource):
  def post(self):
    event = request.get_json()
    logging.info("sales order: received reservation confirmation")
    order = SalesOrder(request.host_url, processId=event["processId"])
    order.confirm(event["reservation"])

api.add_resource(
  SalesOrderReservationConfirmation,
  "/api/salesorder/confirm/reservation"
)
