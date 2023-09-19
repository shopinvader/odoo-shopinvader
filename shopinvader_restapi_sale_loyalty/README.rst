.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=======================
Shopinvader Sale Coupon
=======================

This module extends the functionality of shopinvader to support Coupons
and Promotions from `sale_loyalty` core module.

Not to be confused with `shopinvader_promotion_rule`, that implements
promotion programs from OCA module `sale_promotion_rule`, an alternative
to the core `sale_loyalty` module.

Changes history
===============

**Version 16:**

* A given code can now offer several rewards, and one can choose in each reward among several free products.
  Hence the `apply_coupon` service had to be adapted to allow specifying reward and/or free product to apply.
  It will raise an error if not enough info is specified.
* Due to the previous point the data structure had to be slightly modified:

  - Several promo codes can be applied on a single SO. They are now exposed in `promo_codes`, a string which is a list of all promo codes.

  - Several programs with code can be applied on a single SO. Field `code_promo_program_id` is thus now `code_promo_program_ids` and is a list of items.

  - Program and rewards structure changed in customer's coupons data structure.
* Coupons are not restricted to their assigned partner anymore. What's more,
  coupons that are generated from sale orders are not assigned to the related customer anymore.
  See https://github.com/odoo/odoo/commit/6927dcda9f99db2a4d2f06b32f8d377c17fe2794 for more info.
  It means that it is not possible to retrieve generated coupons from the customer `get` service.

Contributors
------------

* `Camptocamp <https://www.camptocamp.com>`_

  * Iván Todorovich <ivan.todorovich@gmail.com>

* `Acsone <https://www.acsone.eu>`_

  * Marie Lejeune <marie.lejeune@acsone.eu>
