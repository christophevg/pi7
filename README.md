# PI 7

> A 2-hour proof-of-concept of an event-driven order/order-line system, with saga-support for non-sequential event ordering.

## Install && Run

For educational simplicity, all components are hosted within the same application. When run locally, you need to instantiate two workers, to allow the app to talk to itself.

```bash
$ git clone https://github.com/christophevg/pi7
$ cd pi7
$ virtualenv venv
$ . venv/bin/activate
(venv) $ pip install -r requirements.txt
(venv) $ gunicorn --workers=2 pi7:server
```

Alternatively, simply ...

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

**IMPORTANT**: In case you do so, create an environment variable called `INTEGRATION_URL`, containing the URL of you Heroku deploy, e.g. `https://pi7-demo.herokuapp.com`, if you called your app `pi7-demo`.

## Trigger a Request

Visit [http://localhost:8000](http://localhost:8000)...

![the client view](media/home.png)

...and press "Submit" to simulate the submission of a request to order `some hotel` and `a plane`.

When the request was successfully processed, the browser will be redirected to [http://localhost:8000/backend](http://localhost:8000/backend), which represents the backend application. It gives an overview of requested reservations and shows the content of the `salesorder` collection in the document store...

![the backend view with all unconfirmed reservations](media/backend1.png)

You can now `confirm` the reservations, and see the updates propagate to the sales order.

![the backend view with one confirmed and one unconfirmed reservation](media/backend2.png)

![the backend view with all confirmed reservations](media/backend3.png)

Now, feel free to go back to the client-facing part of the application and modify the order, submitting a second request and handle that also ;-) Some inspiration:

```json
{
  "customer" : "koen",
  "reservations" : [
    { "id": 1, "reserved": "some hotel" },
    { "id": 2, "reserved": "a plane" },
    { "id": 3, "reserved": "a bike" }
  ] 
}
```

## Observe Workflow

The logging shows the workflow in action, from the web application receiving the browser request, through the integration layer, dispatching the request to consumers, up to the final confirmation.

```
[2018-11-24 22:02:37 +0100] [6795] [INFO] web: received sales order request
[2018-11-24 22:02:37 +0100] [6795] [INFO]      assigned processId 5f36415b-cd0c-405c-8d44-100ba0cfb82c
[2018-11-24 22:02:37 +0100] [6795] [INFO]      publishing sales order request event
[2018-11-24 22:02:37 +0100] [6794] [INFO] integration: received sales order request
[2018-11-24 22:02:37 +0100] [6794] [INFO]              delivering to sales order and reservation components
[2018-11-24 22:02:37 +0100] [6795] [INFO] sales order: received sales order request
[2018-11-24 22:02:37 +0100] [6795] [INFO] sales order: persisted 2ab2894f-c9de-41fe-bfa7-9794aacd6a19
[2018-11-24 22:02:37 +0100] [6795] [INFO] reservation: received sales order request
[2018-11-24 22:02:37 +0100] [6795] [INFO] reservation: making reservation for some hotel
[2018-11-24 22:02:37 +0100] [6795] [INFO] reservation: persisted 1db8e9d0-1963-4524-abf1-f34c08ed08cc
[2018-11-24 22:02:37 +0100] [6795] [INFO] reservation: making reservation for a plane
[2018-11-24 22:02:37 +0100] [6795] [INFO] reservation: persisted bf076b19-8726-47b6-89be-a0f3a6e86999
[2018-11-24 22:02:56 +0100] [6795] [INFO] reservation: confirming 1db8e9d0-1963-4524-abf1-f34c08ed08cc
[2018-11-24 22:02:56 +0100] [6795] [INFO] reservation: persisted 1db8e9d0-1963-4524-abf1-f34c08ed08cc
[2018-11-24 22:02:56 +0100] [6794] [INFO] integration: received reservation confirmation
[2018-11-24 22:02:56 +0100] [6794] [INFO]              delivering to sales order component
[2018-11-24 22:02:56 +0100] [6795] [INFO] sales order: received reservation confirmation
[2018-11-24 22:02:56 +0100] [6795] [INFO] sales order: persisted 2ab2894f-c9de-41fe-bfa7-9794aacd6a19
[2018-11-24 22:03:06 +0100] [6795] [INFO] reservation: confirming bf076b19-8726-47b6-89be-a0f3a6e86999
[2018-11-24 22:03:06 +0100] [6795] [INFO] reservation: persisted bf076b19-8726-47b6-89be-a0f3a6e86999
[2018-11-24 22:03:06 +0100] [6794] [INFO] integration: received reservation confirmation
[2018-11-24 22:03:06 +0100] [6794] [INFO]              delivering to sales order component
[2018-11-24 22:03:06 +0100] [6795] [INFO] sales order: received reservation confirmation
[2018-11-24 22:03:06 +0100] [6795] [INFO] sales order: persisted 2ab2894f-c9de-41fe-bfa7-9794aacd6a19
[2018-11-24 22:03:06 +0100] [6795] [INFO] sales order: all reservations are confirmed
[2018-11-24 22:03:06 +0100] [6794] [INFO] integration: received sales order confirmation
```

## Meanwhile in the Store

```bash
$ mongo
> use pi7
> db.salesorder.find().pretty()
{
	"_id" : "2ab2894f-c9de-41fe-bfa7-9794aacd6a19",
	"processId" : "5f36415b-cd0c-405c-8d44-100ba0cfb82c",
	"salesorder" : {
		"customer" : "christophe",
		"reservations" : [
			{
				"status" : "confirmed",
				"_id" : "1db8e9d0-1963-4524-abf1-f34c08ed08cc",
				"reserved" : "some hotel",
				"id" : 1
			},
			{
				"status" : "confirmed",
				"_id" : "bf076b19-8726-47b6-89be-a0f3a6e86999",
				"reserved" : "a plane",
				"id" : 2
			}
		]
	}
}
> db.reservation.find().pretty()
{
	"_id" : "1db8e9d0-1963-4524-abf1-f34c08ed08cc",
	"processId" : "5f36415b-cd0c-405c-8d44-100ba0cfb82c",
	"reservation" : {
		"status" : "confirmed",
		"reserved" : "some hotel",
		"id" : 1,
		"history" : [
			{
				"status" : "unconfirmed",
				"time" : 1543093357
			},
			{
				"status" : "confirmed",
				"time" : 1543093376
			}
		]
	}
}
{
	"_id" : "bf076b19-8726-47b6-89be-a0f3a6e86999",
	"processId" : "5f36415b-cd0c-405c-8d44-100ba0cfb82c",
	"reservation" : {
		"status" : "confirmed",
		"reserved" : "a plane",
		"id" : 2,
		"history" : [
			{
				"status" : "unconfirmed",
				"time" : 1543093357
			},
			{
				"status" : "confirmed",
				"time" : 1543093386
			}
		]
	}
}
```
