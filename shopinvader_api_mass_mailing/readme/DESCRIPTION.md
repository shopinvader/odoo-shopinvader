This module adds per endpoint configurable mailing list and two new public routes to
manage the subscription of a contact to the mailing list.

 - `/shopinvader_api/mailing/subscribe` to subscribe a contact to the mailing list
 - `/shopinvader_api/mailing/unsubscribe` to unsubscribe a contact from the mailing list

 A contact here is defined by its email address, no partner is linked or created.

It may be intersting to protect these endpoints with a captcha to avoid abuse,
you could take a look at the `fastapi_captcha` for instance.
