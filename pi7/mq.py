import os
import socket
import logging
import json

from flask           import request
from flask_restful   import Resource

try:
  from urllib.parse import urlparse
except ImportError:
  from urlparse import urlparse

import paho.mqtt.client as mqtt

from pi7             import api

MQTT_URL  = os.environ.get("CLOUDMQTT_URL")
CLOUDMQTT = not MQTT_URL is None
if not CLOUDMQTT:
  MQTT_URL = os.environ.get("MQTT_URL") or "mqtt://localhost:1883"

MQ = urlparse(MQTT_URL)

MQ_WS = {
  "ssl"      : MQ.scheme == "wss" or CLOUDMQTT,
  "hostname" : MQ.hostname,
  "port"     : 30000 + int(str(MQ.port)[-4:]) if CLOUDMQTT else 9001,
  "username" : MQ.username,
  "password" : MQ.password  
}

class MQInfo(Resource):
  def get(self):
    config = MQ_WS
    if config["hostname"] == "localhost":
      s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      try:
        s.connect(("8.8.8.8", 80))
        config["hostname"] = s.getsockname()[0]
      except Exception as e:
        return None
      finally:
        s.close()
    return config

api.add_resource(MQInfo, "/api/mq/connection")


def on_connect(client, client_id, flags, rc):
  logging.debug("connected with result code {0}".format(rc))

def on_disconnect(client, userData, rc):
  logging.error("MQTT broker disconnected")
  broker.loop_stop()
  broker = None

subscriptions = {}

def subscribe(topic, handler):
  if not topic in subscriptions:
    subscriptions[topic] = [ handler ]
  else:
    subscriptions[topic].append(handler)

def on_message(client, client_id, msg):
  topic = msg.topic
  msg   = str(msg.payload.decode("utf-8"))
  if topic in subscriptions:
    for subscriber in subscriptions[topic]:
      try:
        subscriber(json.loads(msg))
      except Exception as e:
        logging.error(e)

logging.debug("connecting to MQ {0}".format(MQ.netloc))
broker = mqtt.Client()
if MQ.username and MQ.password:
  broker.username_pw_set(MQ.username, MQ.password)
broker.on_connect    = on_connect
broker.on_disconnect = on_disconnect
broker.on_message    = on_message

broker.connect(MQ.hostname, MQ.port)
broker.loop_start()

broker.subscribe("#")

def publish(topic, obj):
  broker.publish( topic,
    json.dumps({
      "processId"   : obj.processId,
      "reservation" : obj.marshall(external=True)
    })
  )
