import os
import logging
import uuid
import time

from pymongo import MongoClient

MONGO_URI = os.environ.get("MONGODB_URI")
if not MONGO_URI:
  MONGO_URI = "mongodb://localhost:27017/pi7"

mongo    = MongoClient(MONGO_URI)
database = MONGO_URI.split("/")[-1]
db       = mongo[database]


class Storable(object):
  def __init__(self, guid=None, historic=False):
    self.guid       = guid or str(uuid.uuid4())
    self.processId  = None
    self.object     = {}
    self.historic   = historic
    if guid: self.load()
    self.persisting = False

  def __getitem__(self, key):
    return self.object[key]

  def __setitem__(self, key, value):
    self.object[key] = value

  def __iter__(self):
    return iter(self.object)

  def load(self):
    data = self.collection().find_one({ "_id" : self.guid })
    if data:
      self.processId = data["processId"]
      self.object    = self.unmarshall(data["object"])
      self.log("loaded {0}".format(self.guid))
    return self

  def persist(self):
    self.persisting = True
    if self.historic:
      if not "history" in self.object:
        self.on_initial_history()
    self.collection().update_one({ "_id": self.guid },
      { "$set" : {
        "processId" : self.processId,
        "object"    : self.marshall()
      }}, upsert=True)
    self.log("persisted {0}".format(self.guid))
    self.when_persisted()
    self.persisting = False
    return self

  def in_context_of(self, processId, load=True):
    self.processId = processId
    if load:
      data = self.collection().find_one({ "processId" : self.processId })
      if data:
        self.guid      = data["_id"]
        self.object    = self.unmarshall(data["object"])
        self.log("loaded context {0}".format(self.processId))
    return self

  def make(self, data, persist=True):
    self.object = self.unmarshall(data)
    if persist: self.persist()

  def update_historic(self, update, persist=True):
    if not "history" in self.object:
      self.object["history"] = []
    for key in update:
      self.object[key] = update[key]
    update["time"] = int(time.time())
    self.object["history"].append(update)
    if persist and not self.persisting: self.persist()

  def on_initial_history(self):
    pass

  def unmarshall(self, data):
    return data

  def marshall(self, external=False):
    data = self.object
    if external:
      data["_id"] = self.guid
      if "history" in data: data.pop("history")
    return data

  def when_persisted(self):
    pass

  def log(self, msg, warning=False):
    msg = "{0}: {1}".format(self.__class__.__name__.lower(), msg)
    if warning:
      logging.warn(msg)
    else:
      logging.info(msg)

  def collection(self):
    return db[self.__class__.__name__.lower()]

  @classmethod
  def collection(clz):
    return db[clz.__name__.lower()]


def historic(original_class):
  orig_init = original_class.__init__

  def __init__(self, guid=None):
    orig_init(self, guid=guid, historic=True)

  original_class.__init__ = __init__
  return original_class