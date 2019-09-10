This module add a REST APi for shopinvader to manage quotation.

Customer can convert a cart into a quotation (the typology of the sale order is set to quotation).

Initialy the quotation have the shopinvader_state "estimating". After updating the price manually when the button "sent" on Odoo backend is summited the quotation will be sent by email (natif behaviour) and the shopinvader_state will switch to "estimated".

On Shopinvader site customer can see the state, the amount ... of quotation.
