This module will give you several endpoints for interacting with delivery carrier.
You can play with it with swagger.

* Add a `/set_carrier` route on the `cart_router`: to set a delivery carrier on your cart;
* Create a new `delivery_carrier` router: the route `delivery_carriers` allow to search on delivery carriers. You can filter on a specific cart, or on a specific country and/or zipcode.
* Create a new `deliveries` router: the route `deliveries` allow to search on all deliveries linked to the current partner.
