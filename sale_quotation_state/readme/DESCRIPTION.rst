This module is used in the context of e-commerce project (like shopinvader)


It allows to specify whether your product requires a quotation.
This can be set per "product.template" or per "product.variant"


For example, you have a product where the supplier price fluctuates a lot,
you can not give a public price but your customer should be able to request a quotation.

.. image:: ../static/description/product.png
   :width: 400px
   :alt: Widget in action



On your shopinvader website when a customer has added a product that requires a quotation,
instead of validating the cart it will "request a quotation".



On Odoo Backoffice the menu quotation has been improved and a new state (quotation_state) has been added.
So you can easily process and follow the quotation request from your external system.

.. image:: ../static/description/quotation.png
   :width: 400px
   :alt: Widget in action

