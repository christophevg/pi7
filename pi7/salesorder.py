import logging
import json

from flask           import request
from flask_restful   import Resource

from pi7       import api
from pi7.store import Storable
from pi7.mq    import broker, subscribe, publish

class SalesOrder(Storable):
  def unmarshall(self, salesorder):
    # use the provided salesorder information, but don't override information
    # about reservations, only use placeholders for not yet received
    # reservation information
    reservations = []
    for reservation in salesorder["reservations"]:
      if "reservations" in self:
        for existing in self["reservations"]:
          if reservation["id"] == existing["id"]:
            reservation = existing
      if not "status" in reservation: reservation["status"] = "unconfirmed"
      reservations.append(reservation)
    salesorder["reservations"] = reservations
    return salesorder

  def when_persisted(self):
    # check if sales order is complete...
    # and all reservations are confirmed...
    # if so, raise an event
    if not "customer" in self: return
    if [r for r in self["reservations"] if r["status"] == "unconfirmed"]: return
    self.log("all reservations are confirmed")
    publish("salesorder/confirm", self)

  def confirm(self, reservation):
    # handle the confirmation of a reservation, replacing a placeholder or
    # simply adding it to the list
    if "customer" in self:
      for i, placeholder in enumerate(self["reservations"]):
        if placeholder["id"] == reservation["id"]:
          self["reservations"][i] = reservation
    else:
      self["reservations"].append(reservation)
    self.persist()

# REST API

class SalesOrderStore(Resource):
  def get(self):
    return [ x for x in SalesOrder.collection().find() ]

api.add_resource(
  SalesOrderStore,
  "/api/store/salesorder"
)

# event consumers

def handle_sales_order_request(event):
  logging.info("salesorder: received sales order request")
  SalesOrder().in_context_of(event["processId"]).make(event["salesorder"])

subscribe("salesorder/request", handle_sales_order_request)

def handle_reservation_confirmation(event):
  logging.info("sales order: received reservation confirmation")
  SalesOrder().in_context_of(event["processId"]).confirm(event["reservation"])

subscribe("reservation/confirm", handle_reservation_confirmation)
