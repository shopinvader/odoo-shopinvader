

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
[shopinvader_address](shopinvader_address/) | 18.0.1.0.0 |  | Shopinvader Address: Delivery,Invoicing
[shopinvader_delivery_state](shopinvader_delivery_state/) | 18.0.1.0.0 |  | Shopinvader delivery state
[shopinvader_sale_state](shopinvader_sale_state/) | 18.0.1.0.0 |  | Basic module to implement state for sale order


Unported addons
---------------
addon | version | maintainers | summary
--- | --- | --- | ---
[sale_quotation](sale_quotation/) | 16.0.0.2.0 (unported) |  | Sale Quotation
[shopinvader_address_shipping_note](shopinvader_address_shipping_note/) | 16.0.1.0.0 (unported) |  | Adds a field shipping note on res.partner
[shopinvader_anonymous_partner](shopinvader_anonymous_partner/) | 16.0.2.0.0 (unported) |  | Manage anonymous partners with a cookie.
[shopinvader_api_address](shopinvader_api_address/) | 16.0.1.3.3 (unported) |  | Adds a service to manage shopinvader invoicing and delivery address
[shopinvader_api_address_shipping_note](shopinvader_api_address_shipping_note/) | 16.0.1.0.0 (unported) |  | Adds a shipping note on schemas of services to manage Shipping Addresses
[shopinvader_api_cart](shopinvader_api_cart/) | 16.0.1.5.0 (unported) |  | Cart FastAPI designed to work with the shopinvader-js-cart library see (https://github.com/shopinvader/shopinvader-js-cart)
[shopinvader_api_cart_cancel](shopinvader_api_cart_cancel/) | 16.0.1.0.0 (unported) |  | Cancel cart via Fastapi
[shopinvader_api_cart_options](shopinvader_api_cart_options/) | 16.0.1.0.2 (unported) |  | Add product options to the cart API
[shopinvader_api_cart_step](shopinvader_api_cart_step/) | 16.0.1.0.1 (unported) |  | Track checkout steps on sale cart.
[shopinvader_api_customer](shopinvader_api_customer/) | 16.0.1.1.0 (unported) |  | Adds service to manage shopinvader customer
[shopinvader_api_invoice](shopinvader_api_invoice/) | 16.0.1.0.1 (unported) |  | Provides invoice web api via Fastapi
[shopinvader_api_lead](shopinvader_api_lead/) | 16.0.1.0.1 (unported) |  | Lead FastAPI adding a service for creating CRM leads.
[shopinvader_api_quotation](shopinvader_api_quotation/) | 16.0.1.1.0 (unported) |  | Shopinvader Quotation
[shopinvader_api_sale](shopinvader_api_sale/) | 16.0.1.2.0 (unported) |  | Sale FastApi for exposing sale order
[shopinvader_api_sale_loyalty](shopinvader_api_sale_loyalty/) | 16.0.1.2.0 (unported) |  | FastAPI services to add coupons and loyalties to carts.
[shopinvader_api_security_invoice](shopinvader_api_security_invoice/) | 16.0.1.0.1 (unported) |  | Add security rule to expose invoices
[shopinvader_api_security_sale](shopinvader_api_security_sale/) | 16.0.1.1.1 (unported) |  | Add security rule to expose sale order
[shopinvader_api_settings](shopinvader_api_settings/) | 16.0.1.0.1 (unported) |  | Adds a service to get commont settings
[shopinvader_api_signin_jwt](shopinvader_api_signin_jwt/) | 16.0.2.0.0 (unported) |  | This module adds a signin service with jwt token.
[shopinvader_api_wishlist](shopinvader_api_wishlist/) | 16.0.1.0.2 (unported) |  | Handle shop wishlist
[shopinvader_fastapi_auth_jwt](shopinvader_fastapi_auth_jwt/) | 16.0.1.0.3 (unported) |  | Provide JWT and Anonymous Partner authentication to FastAPI routes.
[shopinvader_fastapi_auth_partner](shopinvader_fastapi_auth_partner/) | 16.0.1.0.0 (unported) |  | Provide Partner and Anonymous Partner authentication to FastAPI routes.
[shopinvader_sale_cart](shopinvader_sale_cart/) | 16.0.1.2.0 (unported) |  | ShopInvader logic for sale carts.
[shopinvader_sale_cart_anonymous_partner](shopinvader_sale_cart_anonymous_partner/) | 16.0.2.0.0 (unported) |  | Glue module between shopinvader_sale_cart and shopinvader_anonymous_partner. This module solves cart conflicts when an anonymous user sign in.
[shopinvader_schema_address](shopinvader_schema_address/) | 16.0.1.3.2 (unported) |  | Adds shchema address: address invoicing_address delivery_address
[shopinvader_schema_invoice](shopinvader_schema_invoice/) | 16.0.1.0.1 (unported) |  | Add schema for invoices
[shopinvader_schema_sale](shopinvader_schema_sale/) | 16.0.1.2.0 (unported) |  | Add schema sale
[shopinvader_schema_sale_state](shopinvader_schema_sale_state/) | 16.0.1.0.1 (unported) |  | Shopinvader Schema Sale State

[//]: # (end addons)

<!-- prettier-ignore-end -->

## Licenses

This repository is licensed under [AGPL-3.0](LICENSE).

However, each module can have a totally different license, as long as they adhere to Shopinvader
policy. Consult each module's `__manifest__.py` file, which contains a `license` key
that explains its license.

----
<!-- /!\ Non OCA Context : Set here the full description of your organization. -->
