This module extends the functionality of Shopinvader to support Coupons
and Promotions from `sale_loyalty` core module.
It is the new version providing FastAPI services.

Not to be confused with `shopinvader_promotion_rule`, that implements
promotion programs from OCA module `sale_promotion_rule`, an alternative
to the core `sale_loyalty` module.

Available services:

* ``/loyalty/{code}`` under the ``loyalty`` router, to get all rewards claimable with a given coupon code
* ``/coupon`` under the ``cart`` router, to apply a given coupon to the cart. Allows to specify which reward and/or which free product to offer.
* ``/reward`` under the ``cart`` router, to apply a given reward (automatic promotion). Note that automatic promotions are applied automatically at cart update, when possible (if no choice must be done). This service allows to apply an automatic promotion for which the reward/free product choice is mandatory.
