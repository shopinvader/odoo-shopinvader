This addons provides 2 new routers: loyalty_router and
sale_loyalty_cart_router. The sale_loyalty_cart_router is declared with
the same tags as the one defined in the shopinvader_api_cart addon. As
this one, no prefix is added to the router, to allow to mount it as a
nested app. See the README of shopinvader_api_cart for more details on
how to do it.

As all api addons, installing this addon will not have any effect on the
existing fastapi app. You must add the routers to the app by yourself by
editing your fastapi.endpoint where you want to add the routes.
