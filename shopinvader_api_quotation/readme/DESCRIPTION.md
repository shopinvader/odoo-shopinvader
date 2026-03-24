This module adds a REST API for shopinvader to manage quotations (see
module: sale_quotation)

Initially, the quotation has the shopinvader_state "estimating". After
updating the price manually when the button "sent" on Odoo backend is
submitted, the quotation will be sent by email (native behaviour) and
the shopinvader_state will switch to "estimated".

On Shopinvader site, the customer can see the state, the amount ... of
quotation.

Why this module and how it can be used?

If you have many different product without price, and these products can
only be selled on demand (compute price, need a seller action). This
module allow your customer to request quotation with products only on
quotation (shop_only_quotation) Your customer can add to cart product
without price and request a quotation for a cart.
