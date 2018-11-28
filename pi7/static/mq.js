(function(globals) {

  var client      = null;
  var clientId    = "client-" + Math.random();
  var connected   = false;
  var subscribers = [];

  function onConnect() {
    console.log("mqtt onConnect");
    connected = true;
    client.subscribe("#");
  }

  function onConnectionLost(responseObject) {
    connected = false;
    if (responseObject.errorCode !== 0) {
      console.log("mqtt onConnectionLost", responseObject);
    }
  }

  function onFailure(invocationContext, errorCode, errorMessage) {
    connected = false;
    console.log("mqtt onFailure", errorMessage);
  }

  function onMessageArrived(message) {
    try {
      var topic   = message.destinationName.split("/"),
          payload = JSON.parse(message.payloadString);
      console.log(topic, payload);
      for(var subscriber in subscribers) {
        subscribers[subscriber](topic, payload);
      }
    } catch(err) {
      console.log("mqtt Failed to parse JSON message: ", err, message);
      return;
    }
  }    

  function connect(mqtt) {
    console.log("mqtt connect using ", mqtt);
    if(! mqtt ) { return; }
    client = new Paho.MQTT.Client(mqtt.hostname, mqtt.port, clientId);

    client.onConnectionLost = onConnectionLost;
    client.onMessageArrived = onMessageArrived;

    var options = {
      useSSL     : mqtt.ssl,
      onSuccess  : onConnect,
      onFailure  : onFailure,
      reconnect  : true,
    }

    if(mqtt.username) {
      options["userName"] = mqtt.username;
      options["password"] = mqtt.password;
    }

    client.connect(options);
  }

  $.get("/api/mq/connection", function(data) {
    connect(data);
  });

  // expose minimal API to send messages
  var api = globals.MQ = {};
  
  api.publish = function publish(topic, msg) {
    if(! connected) {
      console.log("mqtt can't publish messages when not connected");
      return;
    }
    var message = new Paho.MQTT.Message(JSON.stringify(msg));
    message.destinationName = topic;
    message.qos = 1;
    client.send(message);
  }

  api.subscribe = function subscribe(subscriber) {
    subscribers.push(subscriber);
  }

})(window);
