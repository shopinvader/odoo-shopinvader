This module adds a REST API for shopinvader to manage quotations.

The Customer can convert a cart into a quotation (the typology of the sale
order is set to quotation).

Initially, the quotation has the `shopinvader_state` "estimating".
After updating the price manually when the button "sent" on Odoo backend
is summited, the quotation will be sent by email (native behaviour) and the
shopinvader_state will switch to "estimated".

On Shopinvader site, the customer can see the state, the amount ... of quotation.

When the backend user sends the quotation, this is visible to the shop
if the backend is set to "Expose all quotations".

If a quotation, previously not bound to any backend, is confirmed from the shop,
then it gets bound to the shop backend automatically.
