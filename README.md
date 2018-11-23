# PI 7

> A 2-hour proof-of-concept of an event-driven order/order-line system, with saga-support for non-sequential event ordering.

## Install && Run

For educational simplicity, all components are hosted within the same application. All communication is done synchronously, again for educational simplicity. So 6 workers are required.

```bash
$ git clone https://github.com/christophevg/pi7
$ cd pi7
$ virtualenv venv
$ . venv/bin/activate
(venv) $ pip install -r requirements.txt
(venv) $ gunicorn --workers=6 pi7:server
```

## Trigger a Request

Visit [http://localhost:8000](http://localhost:8000)...

![the browser client](media/browser.png)

...and press "Submit".

## Observe Workflow

The logging shows the workflow in action, from the web application receiving the browser request, through the integration layer, dispatching the request to consumers, up to the final confirmation.

```
[2018-11-23 20:57:40 +0100] [92999] [INFO] web: received sales order request
[2018-11-23 20:57:40 +0100] [92999] [INFO]      assigned businessProcessId 2a71565f-91c3-4cbc-9fdf-00ae095eb0be
[2018-11-23 20:57:40 +0100] [92999] [INFO]      publishing sales order request event
[2018-11-23 20:57:40 +0100] [93000] [INFO] integration: received sales order request
[2018-11-23 20:57:40 +0100] [93000] [INFO]              delivering to sales order and reservation components
[2018-11-23 20:57:40 +0100] [92997] [INFO] sales order: received sales order request
[2018-11-23 20:57:40 +0100] [92997] [INFO] sales order: persisted 28b5255b-f194-451f-971c-93c44f403ee7
[2018-11-23 20:57:40 +0100] [92997] [INFO] reservation: received sales order request
[2018-11-23 20:57:40 +0100] [92997] [INFO] reservation: making reservation for some hotel
[2018-11-23 20:57:41 +0100] [92997] [INFO] reservation: confirming
[2018-11-23 20:57:41 +0100] [92995] [INFO] integration: received reservation confirmation
[2018-11-23 20:57:41 +0100] [92995] [INFO]              delivering to sales order component
[2018-11-23 20:57:41 +0100] [93002] [INFO] sales order: received reservation confirmation
[2018-11-23 20:57:41 +0100] [93002] [INFO] sales order: persisted 28b5255b-f194-451f-971c-93c44f403ee7
[2018-11-23 20:57:41 +0100] [92997] [INFO] reservation: making reservation for a plane
[2018-11-23 20:57:42 +0100] [92997] [INFO] reservation: confirming
[2018-11-23 20:57:42 +0100] [93002] [INFO] integration: received reservation confirmation
[2018-11-23 20:57:42 +0100] [93002] [INFO]              delivering to sales order component
[2018-11-23 20:57:43 +0100] [93001] [INFO] sales order: received reservation confirmation
[2018-11-23 20:57:43 +0100] [93001] [INFO] sales order: persisted 28b5255b-f194-451f-971c-93c44f403ee7
[2018-11-23 20:57:43 +0100] [93001] [INFO] sales order: all reservations are confirmed
[2018-11-23 20:57:43 +0100] [92996] [INFO] integration: received sales order confirmation
```

## Meanwhile in the Store

```bash
$ mongo
> use pi7
> db.salesorder.find().pretty()
{
	"_id" : "28b5255b-f194-451f-971c-93c44f403ee7",
	"origin" : "http://localhost:8000/",
	"processId" : "2a71565f-91c3-4cbc-9fdf-00ae095eb0be",
	"salesorder" : {
		"customer" : "christophe",
		"reservations" : [
			{
				"status" : "confirmed",
				"reserved" : "some hotel",
				"id" : 1
			},
			{
				"status" : "confirmed",
				"reserved" : "a plane",
				"id" : 2
			}
		],
		"made" : true
	}
}
```