A cron job "Compute new products" comes with this module, it can be configured.
It runs every day and flags as 'new' the last (50 by default) shopinvader products created.
The method 'compute_new_product' used by this job takes two arguments:

* The maximum number of product to flag.
* Extra domain for searching the products.
