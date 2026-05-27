

# Shopinvader
<!-- /!\ Non OCA Context : Set here the badge of your runbot / runboat instance. -->
[![Pre-commit Status](https://github.com/shopinvader/odoo-shopinvader/actions/workflows/pre-commit.yml/badge.svg?branch=18.0)](https://github.com/shopinvader/odoo-shopinvader/actions/workflows/pre-commit.yml?query=branch%3A18.0)
[![Build Status](https://github.com/shopinvader/odoo-shopinvader/actions/workflows/test.yml/badge.svg?branch=18.0)](https://github.com/shopinvader/odoo-shopinvader/actions/workflows/test.yml?query=branch%3A18.0)
[![codecov](https://codecov.io/gh/shopinvader/odoo-shopinvader/branch/18.0/graph/badge.svg)](https://codecov.io/gh/shopinvader/odoo-shopinvader)
<!-- /!\ Non OCA Context : Set here the badge of your translation instance. -->

<!-- /!\ do not modify above this line -->

Odoo REST APIs for e-commerce.

<!-- /!\ do not modify below this line -->

<!-- prettier-ignore-start -->

[//]: # (addons)

Available addons
----------------
addon | version | maintainers | summary
--- | --- | --- | ---
[sale_cart](sale_cart/) | 18.0.1.0.0 |  | Use Sale Orders as cart.
[sale_cart_step](sale_cart_step/) | 18.0.1.0.0 |  | Track checkout steps on sale cart.
[sale_quotation](sale_quotation/) | 18.0.1.0.0 |  | Sale Quotation
[shopinvader_address](shopinvader_address/) | 18.0.1.0.0 |  | Shopinvader Address: Delivery,Invoicing
[shopinvader_address_shipping_note](shopinvader_address_shipping_note/) | 18.0.1.0.0 |  | Adds a field shipping note on res.partner
[shopinvader_anonymous_partner](shopinvader_anonymous_partner/) | 18.0.1.0.0 |  | Manage anonymous partners with a cookie.
[shopinvader_api_address](shopinvader_api_address/) | 18.0.1.0.0 |  | Adds a service to manage shopinvader invoicing and delivery address
[shopinvader_api_address_shipping_note](shopinvader_api_address_shipping_note/) | 18.0.1.0.0 |  | Adds a shipping note on schemas of services to manage Shipping Addresses
[shopinvader_api_cart](shopinvader_api_cart/) | 18.0.1.0.1 |  | Cart FastAPI designed to work with the shopinvader-js-cart library see (https://github.com/shopinvader/shopinvader-js-cart)
[shopinvader_api_cart_cancel](shopinvader_api_cart_cancel/) | 18.0.1.0.0 |  | Cancel cart via Fastapi
[shopinvader_api_cart_options](shopinvader_api_cart_options/) | 18.0.1.0.0 |  | Add product options to the cart API
[shopinvader_api_cart_step](shopinvader_api_cart_step/) | 18.0.1.0.0 |  | Track checkout steps on sale cart.
[shopinvader_api_customer](shopinvader_api_customer/) | 18.0.1.0.0 |  | Adds service to manage shopinvader customer
[shopinvader_api_invoice](shopinvader_api_invoice/) | 18.0.1.0.0 |  | Provides invoice web api via Fastapi
[shopinvader_api_lead](shopinvader_api_lead/) | 18.0.1.0.0 |  | Lead FastAPI adding a service for creating CRM leads.
[shopinvader_api_mass_mailing](shopinvader_api_mass_mailing/) | 18.0.1.0.0 | <a href='https://github.com/paradoxxxzero'><img src='https://github.com/paradoxxxzero.png' width='32' height='32' style='border-radius:50%;' alt='paradoxxxzero'/></a> | Add a way to subscribe/unsubscribe to mass mailing list of an endpoint
[shopinvader_api_quotation](shopinvader_api_quotation/) | 18.0.1.0.0 |  | Shopinvader Quotation
[shopinvader_api_sale](shopinvader_api_sale/) | 18.0.1.0.0 |  | Sale FastApi for exposing sale order
[shopinvader_api_sale_loyalty](shopinvader_api_sale_loyalty/) | 18.0.1.0.0 |  | FastAPI services to add coupons and loyalties to carts.
[shopinvader_api_security_invoice](shopinvader_api_security_invoice/) | 18.0.1.0.0 |  | Add security rule to expose invoices
[shopinvader_api_security_sale](shopinvader_api_security_sale/) | 18.0.1.0.0 |  | Add security rule to expose sale order
[shopinvader_api_settings](shopinvader_api_settings/) | 18.0.1.0.0 |  | Adds a service to get commont settings
[shopinvader_api_signin_jwt](shopinvader_api_signin_jwt/) | 18.0.1.0.0 |  | This module adds a signin service with jwt token.
[shopinvader_api_warehouse](shopinvader_api_warehouse/) | 18.0.1.0.0 | <a href='https://github.com/paradoxxxzero'><img src='https://github.com/paradoxxxzero.png' width='32' height='32' style='border-radius:50%;' alt='paradoxxxzero'/></a> | Adds sales warehouse information to Shopinvader API
[shopinvader_api_wishlist](shopinvader_api_wishlist/) | 18.0.1.0.0 |  | Handle shop wishlist
[shopinvader_delivery_state](shopinvader_delivery_state/) | 18.0.1.0.0 |  | Shopinvader delivery state
[shopinvader_fastapi_auth_jwt](shopinvader_fastapi_auth_jwt/) | 18.0.1.0.0 |  | Provide JWT and Anonymous Partner authentication to FastAPI routes.
[shopinvader_fastapi_auth_partner](shopinvader_fastapi_auth_partner/) | 18.0.1.0.0 |  | Provide Partner and Anonymous Partner authentication to FastAPI routes.
[shopinvader_router_helper](shopinvader_router_helper/) | 18.0.1.0.1 |  | Standard helper for shopinvader routers
[shopinvader_sale_cart](shopinvader_sale_cart/) | 18.0.1.0.0 |  | ShopInvader logic for sale carts.
[shopinvader_sale_cart_anonymous_partner](shopinvader_sale_cart_anonymous_partner/) | 18.0.1.0.0 |  | Glue module between shopinvader_sale_cart and shopinvader_anonymous_partner. This module solves cart conflicts when an anonymous user sign in.
[shopinvader_sale_channel](shopinvader_sale_channel/) | 18.0.1.0.0 | <a href='https://github.com/paradoxxxzero'><img src='https://github.com/paradoxxxzero.png' width='32' height='32' style='border-radius:50%;' alt='paradoxxxzero'/></a> | Adds sale channel management to Shopinvader
[shopinvader_sale_state](shopinvader_sale_state/) | 18.0.1.0.0 |  | Basic module to implement state for sale order
[shopinvader_schema_address](shopinvader_schema_address/) | 18.0.1.0.0 |  | Adds schema address: address invoicing_address delivery_address
[shopinvader_schema_invoice](shopinvader_schema_invoice/) | 18.0.1.0.0 |  | Add schema for invoices
[shopinvader_schema_sale](shopinvader_schema_sale/) | 18.0.1.0.0 |  | Add schema sale
[shopinvader_schema_sale_state](shopinvader_schema_sale_state/) | 18.0.1.0.0 |  | Shopinvader Schema Sale State

[//]: # (end addons)

<!-- prettier-ignore-end -->

## Licenses

This repository is licensed under [AGPL-3.0](LICENSE).

However, each module can have a totally different license, as long as they adhere to Shopinvader
policy. Consult each module's `__manifest__.py` file, which contains a `license` key
that explains its license.

----
<!-- /!\ Non OCA Context : Set here the full description of your organization. -->
