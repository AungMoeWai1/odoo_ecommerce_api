# Firebase Sync Log

This Odoo addon sends Firebase Cloud Messaging (FCM) push notifications to
devices registered for Odoo users and stores a notification log in Odoo.

## Requirements

- Odoo 19
- Python package `firebase-admin`
- A Firebase project with Cloud Messaging enabled
- A Firebase service-account key file named `hr_intellect.json`

Install the Python dependency in the same environment used by Odoo:

```bash
pip install firebase-admin
```

## Firebase configuration

1. Open the Firebase Console and select the Firebase project used by the app.
2. Go to **Project settings > Service accounts**.
3. Generate a new private key for the Firebase Admin SDK.
4. Rename the downloaded file to `hr_intellect.json`.
5. Place it at:

```text
firebase_sync_log/key/hr_intellect.json
```

The connector reads this default file automatically. The path is resolved from
the addon directory, so it also works when the addon is installed in a custom
Odoo addons path.

### Service-account key security

`hr_intellect.json` contains private credentials. Do not commit it to Git,
publish it in the addon archive, or expose it through a web server. Copy it
into the deployment environment separately and restrict its file permissions:

```bash
chmod 600 firebase_sync_log/key/hr_intellect.json
```

Add the key to `.gitignore` in the repository that contains this addon:

```gitignore
firebase_sync_log/key/*.json
```

If the key has already been committed or exposed, revoke it in Firebase and
generate a replacement key.

## Odoo configuration

1. Add `firebase_sync_log` to the Odoo addons path.
2. Update the Apps list.
3. Install **Firebase Notification for Odoo Ecommerce Order**.
4. Confirm that the dependent addon is installed before using the helper from
	 another addon.

The notification helper reads device tokens from the Odoo user record:

- `mobile_device_token` for one token
- `mobile_device_tokens`, with a `token` field, for multiple tokens

The mobile application must register its FCM token on the corresponding Odoo
user before a notification can be delivered.

## Usage from another Odoo addon

Import the notification module:

```python
from odoo.addons.firebase_sync_log.models import message_notifications
```

Then call `send_message_notification` with the recipient user, the Odoo
record that caused the event, a title, and a message body:

```python
message_notifications.send_message_notification(
		self.partner_id.user_ids[:1],
		self,
		"Sale order has been confirmed",
		f"Your order {self.name} has been confirmed!",
)
```

Example inside a model method:

```python
from odoo import models

from odoo.addons.firebase_sync_log.models import message_notifications


class SaleOrder(models.Model):
		_inherit = "sale.order"

		def action_confirm(self):
				result = super().action_confirm()
				for order in self:
						user = order.partner_id.user_ids[:1]
						if user:
								message_notifications.send_message_notification(
										user,
										order,
										"Sale order has been confirmed",
										f"Your order {order.name} has been confirmed!",
								)
				return result
```

The helper returns `True` when at least one notification is sent successfully
and `False` when no device token exists or Firebase cannot send the message.
Each attempt is recorded in the notification log model.
