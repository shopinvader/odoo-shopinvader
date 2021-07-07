This module adds a REST API for shopinvader to manage quotations.

The Customer can convert a cart into a quotation (the typology of the sale
order is set to quotation).

Initialy, the quotation has the `shopinvader_state` "estimating".
After updating the price manually when the button "sent" on Odoo backend
is summited, the quotation will be sent by email (native behaviour) and the
shopinvader_state will switch to "estimated".

On Shopinvader site, the customer can see the state, the amount ... of quotation.
