This module is a glue module between *shopinvader_sale_channel* and *sale_channel_catalog*

All the products with *sale_ok* of the catalog are available to be sold on the *shopinvader backend*.

-----------------
About basic rules
-----------------

If you want to forbid the addition of product in sale order (cart), unflag *sale_ok* (Can be Sold) on the product or remove it from the catalog.

--------------------
About advanced rules
--------------------

You may want to restrict a bit more the products based on some rules.
Like products on the catalog (published on the website) but not allowed to buy
based on some business rules (quantity in stock to low, product not launched yet, etc.)

The recommanded practice is to allow the customer to add the product in his cart (sale_order), mark the sale order line as exception and disallow the sale confirmation (checkout).

Because in some context, a cart may can have a long lifecycle before the checkout, stock level may changes, or you may allow pre-order of products.

The current module do not implement these restrictions.
