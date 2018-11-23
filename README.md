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

![the browser client](media/browser.png)

...and press "Submit". When the request was successfully processed, the browser will be redirected to [http://localhost:8000/store](http://localhost:8000/store), which will show the content of the `salesorder` collection in the document store...

![the browser store](media/store.png)

## Observe Workflow

The logging shows the workflow in action, from the web application receiving the browser request, through the integration layer, dispatching the request to consumers, up to the final confirmation.

```
[2018-11-23 23:53:09 +0100] [1859] [INFO] web: received sales order request
[2018-11-23 23:53:09 +0100] [1859] [INFO]      assigned processId f26c2895-16d5-4fb4-8b5f-44df59d36508
[2018-11-23 23:53:09 +0100] [1859] [INFO]      publishing sales order request event
[2018-11-23 23:53:09 +0100] [1858] [INFO] integration: received sales order request
[2018-11-23 23:53:09 +0100] [1858] [INFO]              delivering to sales order and reservation components
[2018-11-23 23:53:09 +0100] [1859] [INFO] sales order: received sales order request
[2018-11-23 23:53:09 +0100] [1859] [INFO] sales order: persisted fee44eef-3580-4d63-9848-3e2226d274b1
[2018-11-23 23:53:09 +0100] [1859] [INFO] reservation: received sales order request
[2018-11-23 23:53:09 +0100] [1859] [INFO] reservation: making reservation for some hotel
[2018-11-23 23:53:10 +0100] [1859] [INFO] reservation: persisted 47235a73-8371-4b80-b35e-c1222bf79ac8
[2018-11-23 23:53:10 +0100] [1859] [INFO] reservation: confirming
[2018-11-23 23:53:10 +0100] [1859] [INFO] reservation: persisted 47235a73-8371-4b80-b35e-c1222bf79ac8
[2018-11-23 23:53:10 +0100] [1858] [INFO] integration: received reservation confirmation
[2018-11-23 23:53:10 +0100] [1858] [INFO]              delivering to sales order component
[2018-11-23 23:53:10 +0100] [1859] [INFO] reservation: making reservation for a plane
[2018-11-23 23:53:11 +0100] [1859] [INFO] reservation: persisted 42fdd97c-474e-4a8f-a78d-3e0cf58cda02
[2018-11-23 23:53:11 +0100] [1859] [INFO] reservation: confirming
[2018-11-23 23:53:11 +0100] [1859] [INFO] reservation: persisted 42fdd97c-474e-4a8f-a78d-3e0cf58cda02
[2018-11-23 23:53:11 +0100] [1858] [INFO] integration: received reservation confirmation
[2018-11-23 23:53:11 +0100] [1858] [INFO]              delivering to sales order component
[2018-11-23 23:53:11 +0100] [1859] [INFO] sales order: received reservation confirmation
[2018-11-23 23:53:11 +0100] [1859] [INFO] sales order: persisted fee44eef-3580-4d63-9848-3e2226d274b1
[2018-11-23 23:53:11 +0100] [1859] [INFO] sales order: received reservation confirmation
[2018-11-23 23:53:11 +0100] [1859] [INFO] sales order: persisted fee44eef-3580-4d63-9848-3e2226d274b1
[2018-11-23 23:53:11 +0100] [1859] [INFO] sales order: all reservations are confirmed
[2018-11-23 23:53:11 +0100] [1858] [INFO] integration: received sales order confirmation
```

## Meanwhile in the Store

```bash
$ mongo
> use pi7
> db.salesorder.find().pretty()
{
	"_id" : "fee44eef-3580-4d63-9848-3e2226d274b1",
	"processId" : "f26c2895-16d5-4fb4-8b5f-44df59d36508",
	"salesorder" : {
		"customer" : "christophe",
		"reservations" : [
			{
				"status" : "confirmed",
				"_id" : "47235a73-8371-4b80-b35e-c1222bf79ac8",
				"reserved" : "some hotel",
				"id" : 1
			},
			{
				"status" : "confirmed",
				"_id" : "42fdd97c-474e-4a8f-a78d-3e0cf58cda02",
				"reserved" : "a plane",
				"id" : 2
			}
		]
	}
}
> db.reservation.find().pretty()
{
	"_id" : "47235a73-8371-4b80-b35e-c1222bf79ac8",
	"processId" : "f26c2895-16d5-4fb4-8b5f-44df59d36508",
	"reservation" : {
		"status" : "confirmed",
		"reserved" : "some hotel",
		"id" : 1
	}
}
{
	"_id" : "42fdd97c-474e-4a8f-a78d-3e0cf58cda02",
	"processId" : "f26c2895-16d5-4fb4-8b5f-44df59d36508",
	"reservation" : {
		"status" : "confirmed",
		"reserved" : "a plane",
		"id" : 2
	}
}
```
