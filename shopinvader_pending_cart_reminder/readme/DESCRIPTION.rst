Relaunch the customer by email, when the cart is not confirmed yet.

When a cart is created by a customer and there is no more activity on it, an
email can be automatically send to the customer to relaunch it.
On the shopinvader backend, you can specify an email template to use and also
the inactive delay before trigger it.

This feature works only for cart related to a logged user and for unconfirmed
cart.
The inactive delay is based on the write_date field.
You can disable this behavior by disable the cron job (so disabled for every
shopinvader backends) or for only 1 backend if you set the quotation_reminder
field to 0 (or less).

When this behavior is disabled (so quotation_reminder <= 0) and then enabled
(so quotation_reminder > 0), the reminder_start_date field is automatically
updated with the current date. This specific behavior is done to avoid sending
email related to old SO.

**Examples:**
You have a cart from last year (not validated). Then the user enable the
quotation reminder. The cron will send an email related to this
old cart (in case of we don't have a start date).

Other case: The reminder behavior is enabled. Then the user disable it for
3 months (by setting the quotation_reminder to 0). During these 3 months, 10
cart has been created by customers. After these 3 months, the user re-enable
the reminder behavior. To avoid sending emails related to these 3 months,
we have to update the reminder_start_date at the date of the quotation_reminder
has been updated (>= 0).
