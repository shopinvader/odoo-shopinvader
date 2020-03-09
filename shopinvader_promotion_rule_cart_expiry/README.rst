.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=========================================
Shopinvader Promotion Rules - Cart Expiry
=========================================

This module fix the incompatibility between shopinvader_promotion_rule and
shopinvader_cart_expiry.
The shopinvader_cart_expiry use the write date to know the last modification done on a
cart. But the shopinvader_promotion_rule update every days (depending on the cron)
promotions applied on a cart. So even if nobody update the cart, the write_date is
updated.

So this module add a specific write_date (shopinvader_write_date) who has exactly the
same behavior of the original field. Except that depending on the context, it's
possible to don't update it (for this case: during the promotion's recompute).

Credits
=======

Contributors
------------

* François Honoré <francois.honore@acsone.eu>
