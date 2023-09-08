This module removes the need of shopinvader variants.
Until they are removed from shopinvader module, the product
view will have a semi-broken shopinvader backend support.

Also, some def as _add_to_cart_allowed are not calling
super because of the shopinvader binding logic changed.
