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
[2018-11-23 22:09:09 +0100] [96760] [INFO] web: received sales order request
[2018-11-23 22:09:09 +0100] [96760] [INFO]      assigned businessProcessId f8df6586-e389-4685-adc1-5b43e9447b26
[2018-11-23 22:09:09 +0100] [96760] [INFO]      publishing sales order request event
[2018-11-23 22:09:09 +0100] [96758] [INFO] integration: received sales order request
[2018-11-23 22:09:09 +0100] [96758] [INFO]              delivering to sales order and reservation components
[2018-11-23 22:09:09 +0100] [96761] [INFO] sales order: received sales order request
[2018-11-23 22:09:09 +0100] [96761] [INFO] sales order: persisted d44d21bc-47b7-46a1-a063-f9412bf9246d
[2018-11-23 22:09:09 +0100] [96759] [INFO] reservation: received sales order request
[2018-11-23 22:09:09 +0100] [96759] [INFO] reservation: making reservation for some hotel
[2018-11-23 22:09:10 +0100] [96759] [INFO] reservation: confirming
[2018-11-23 22:09:10 +0100] [96761] [INFO] integration: received reservation confirmation
[2018-11-23 22:09:10 +0100] [96761] [INFO]              delivering to sales order component
[2018-11-23 22:09:10 +0100] [96757] [INFO] sales order: received reservation confirmation
[2018-11-23 22:09:10 +0100] [96757] [INFO] sales order: persisted d44d21bc-47b7-46a1-a063-f9412bf9246d
[2018-11-23 22:09:10 +0100] [96759] [INFO] reservation: making reservation for a plane
[2018-11-23 22:09:11 +0100] [96759] [INFO] reservation: confirming
[2018-11-23 22:09:11 +0100] [96756] [INFO] integration: received reservation confirmation
[2018-11-23 22:09:11 +0100] [96756] [INFO]              delivering to sales order component
[2018-11-23 22:09:11 +0100] [96761] [INFO] sales order: received reservation confirmation
[2018-11-23 22:09:11 +0100] [96761] [INFO] sales order: persisted d44d21bc-47b7-46a1-a063-f9412bf9246d
[2018-11-23 22:09:11 +0100] [96761] [INFO] sales order: all reservations are confirmed
[2018-11-23 22:09:11 +0100] [96757] [INFO] integration: received sales order confirmation
```

## Meanwhile in the Store

```bash
$ mongo
> use pi7
> db.salesorder.find().pretty()
{
	"_id" : "d44d21bc-47b7-46a1-a063-f9412bf9246d",
	"processId" : "f8df6586-e389-4685-adc1-5b43e9447b26",
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