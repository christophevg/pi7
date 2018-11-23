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
[2018-11-23 22:58:13 +0100] [99129] [INFO] web: received sales order request
[2018-11-23 22:58:13 +0100] [99129] [INFO]      assigned businessProcessId 26c98925-57fc-4dff-99e2-5913a71e5099
[2018-11-23 22:58:13 +0100] [99129] [INFO]      publishing sales order request event
[2018-11-23 22:58:13 +0100] [99128] [INFO] integration: received sales order request
[2018-11-23 22:58:13 +0100] [99128] [INFO]              delivering to sales order and reservation components
[2018-11-23 22:58:13 +0100] [99126] [INFO] sales order: received sales order request
[2018-11-23 22:58:13 +0100] [99126] [INFO] sales order: persisted 078333e2-0b1f-4d04-8429-f057a4c09cf2
[2018-11-23 22:58:13 +0100] [99130] [INFO] reservation: received sales order request
[2018-11-23 22:58:13 +0100] [99130] [INFO] reservation: making reservation for some hotel
[2018-11-23 22:58:14 +0100] [99130] [INFO] reservation: confirming
[2018-11-23 22:58:14 +0100] [99126] [INFO] integration: received reservation confirmation
[2018-11-23 22:58:14 +0100] [99126] [INFO]              delivering to sales order component
[2018-11-23 22:58:14 +0100] [99125] [INFO] sales order: received reservation confirmation
[2018-11-23 22:58:14 +0100] [99125] [INFO] sales order: persisted 078333e2-0b1f-4d04-8429-f057a4c09cf2
[2018-11-23 22:58:14 +0100] [99130] [INFO] reservation: making reservation for a plane
[2018-11-23 22:58:15 +0100] [99130] [INFO] reservation: confirming
[2018-11-23 22:58:15 +0100] [99126] [INFO] integration: received reservation confirmation
[2018-11-23 22:58:15 +0100] [99126] [INFO]              delivering to sales order component
[2018-11-23 22:58:16 +0100] [99125] [INFO] sales order: received reservation confirmation
[2018-11-23 22:58:16 +0100] [99125] [INFO] sales order: persisted 078333e2-0b1f-4d04-8429-f057a4c09cf2
[2018-11-23 22:58:16 +0100] [99125] [INFO] sales order: all reservations are confirmed
[2018-11-23 22:58:16 +0100] [99127] [INFO] integration: received sales order confirmation
```

## Meanwhile in the Store

```bash
$ mongo
> use pi7
> db.salesorder.find().pretty()
{
	"_id" : "078333e2-0b1f-4d04-8429-f057a4c09cf2",
	"processId" : "26c98925-57fc-4dff-99e2-5913a71e5099",
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
		]
	}
}
```