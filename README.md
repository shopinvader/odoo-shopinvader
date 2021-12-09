[![Build Status](https://travis-ci.org/shopinvader/odoo-shopinvader.svg?branch=13.0)](https://travis-ci.org/shopinvader/odoo-shopinvader)
[![codecov](https://codecov.io/gh/shopinvader/odoo-shopinvader/branch/13.0/graph/badge.svg)](https://codecov.io/gh/shopinvader/odoo-shopinvader/branch/13.0)
[![Code Climate](https://codeclimate.com/github/shopinvader/odoo-shopinvader/badges/gpa.svg)](https://codeclimate.com/github/shopinvader/odoo-shopinvader)


ShopInvader
=================

Web alternative solution based on locomotivecms

Documentation
===============

A work in progress documentation is available here : https://akretion.github.io/shopinvader-documentation

[//]: # (addons)

Available addons
----------------
addon | version | maintainers | summary
--- | --- | --- | ---
[base_url](base_url/) | 14.0.1.0.1 |  | keep history of url for products & categories
[shopinvader](shopinvader/) | 14.0.5.5.1 |  | Shopinvader
[shopinvader_algolia](shopinvader_algolia/) | 14.0.2.0.0 |  | Shopinvader Algolia Connector
[shopinvader_assortment](shopinvader_assortment/) | 14.0.1.2.0 |  | Shopinvader Assortment
[shopinvader_auth_api_key](shopinvader_auth_api_key/) | 14.0.1.0.5 |  | Shopinvader API_KEY Authentication
[shopinvader_auth_jwt](shopinvader_auth_jwt/) | 14.0.1.0.3 |  | Find shopinvader backend and partner from JWT token
[shopinvader_backend_image_proxy](shopinvader_backend_image_proxy/) | 14.0.1.0.1 |  | Add possibility to replace the image URL by the proxy url set on the SE backend
[shopinvader_cart_expiry](shopinvader_cart_expiry/) | 14.0.1.0.0 |  | Shopinvader module to manage an expiry delay on cart
[shopinvader_category_image_for_product](shopinvader_category_image_for_product/) | 14.0.1.0.1 |  | Shopinvader Display category image for product
[shopinvader_customer_invoicing_mode](shopinvader_customer_invoicing_mode/) | 14.0.1.0.0 |  | Glue module to expose the invoicing_mode field to shopinvader
[shopinvader_customer_multi_user](shopinvader_customer_multi_user/) | 14.0.1.3.0 |  | Enable registration of multiple users per each company customer.
[shopinvader_customer_multi_user_company_group](shopinvader_customer_multi_user_company_group/) | 14.0.1.0.0 |  | Share shopinvader records within the Company Group
[shopinvader_customer_multi_user_validate](shopinvader_customer_multi_user_validate/) | 14.0.1.1.0 |  | Glue module for `shopinvader_customer_validate` and `shopinvader_customer_multi_user`.
[shopinvader_customer_multi_user_wishlist](shopinvader_customer_multi_user_wishlist/) | 14.0.1.0.0 |  | Integrate customer multi user and wishlist.
[shopinvader_customer_price](shopinvader_customer_price/) | 14.0.1.0.0 |  | Expose customer's specific prices.
[shopinvader_customer_price_wishlist](shopinvader_customer_price_wishlist/) | 14.0.1.0.0 |  | Expose customer's specific prices.
[shopinvader_customer_validate](shopinvader_customer_validate/) | 14.0.1.2.0 |  | Provide configuration and machinery to validate customers.
[shopinvader_delivery_carrier](shopinvader_delivery_carrier/) | 14.0.2.1.0 |  | Carrier integration for Shopinvader
[shopinvader_easy_binding](shopinvader_easy_binding/) | 14.0.1.0.1 | [![ivantodorovich](https://github.com/ivantodorovich.png?size=30px)](https://github.com/ivantodorovich) | Easily manage Shopinvader bindings for your company backend.
[shopinvader_elasticsearch](shopinvader_elasticsearch/) | 14.0.3.0.0 |  | Shopinvader Elasticsearch Connector
[shopinvader_guest_mode](shopinvader_guest_mode/) | 14.0.1.0.1 |  | Guest mode for Shopinvader
[shopinvader_image](shopinvader_image/) | 14.0.1.1.2 |  | Add the export of Image for Shopinvader
[shopinvader_import_image](shopinvader_import_image/) | 14.0.1.1.1 |  | Import product images
[shopinvader_invoice](shopinvader_invoice/) | 14.0.2.1.2 |  | Shopinvader Invoice module
[shopinvader_lead](shopinvader_lead/) | 14.0.1.0.0 |  | Shopinvader Lead Management
[shopinvader_locomotive](shopinvader_locomotive/) | 14.0.2.0.0 |  | Manage communications between Shopinvader and Locomotive CMS
[shopinvader_locomotive_algolia](shopinvader_locomotive_algolia/) | 14.0.1.0.0 |  | This addons is used to push the initial algolia configuration to locomotive
[shopinvader_locomotive_guest_mode](shopinvader_locomotive_guest_mode/) | 14.0.1.0.2 |  | Shopinvader guest mode for locomotive
[shopinvader_locomotive_reset_password](shopinvader_locomotive_reset_password/) | 14.0.1.0.1 |  | Give the possibility to send a email to reset thepassword from odoo
[shopinvader_locomotive_sale_profile](shopinvader_locomotive_sale_profile/) | 14.0.1.0.0 |  | Synchronize the sale profile info to customer record on Locomotive
[shopinvader_locomotive_wishlist](shopinvader_locomotive_wishlist/) | 14.0.1.0.1 |  | Synchronize wishlist details to Locomotive users record.
[shopinvader_membership](shopinvader_membership/) | 14.0.1.0.1 |  | Shopinvader Membership module
[shopinvader_multi_cart](shopinvader_multi_cart/) | 14.0.1.1.0 |  | Manage multiple carts in Shopinvader
[shopinvader_multi_category](shopinvader_multi_category/) | 14.0.1.0.0 |  | Shopinvader Many Categories
[shopinvader_notification_default](shopinvader_notification_default/) | 14.0.1.0.0 |  | Provide default notification templates for Shopinvader suite.
[shopinvader_partner_firstname](shopinvader_partner_firstname/) | 14.0.1.0.0 |  | Shopinvader Customer firstname/lastname
[shopinvader_partner_vat](shopinvader_partner_vat/) | 14.0.1.0.1 |  | Shopinvader Check VAT with invader environnement
[shopinvader_pending_cart_reminder](shopinvader_pending_cart_reminder/) | 14.0.1.0.0 |  | Shopinvader module to relaunch the customer when the cart/sale is not confirmed yet. Configure the delay and the email template on the backend.
[shopinvader_portal_mode](shopinvader_portal_mode/) | 14.0.1.0.0 |  | Shopinvader portal mode
[shopinvader_pos](shopinvader_pos/) | 14.0.2.2.0 |  | Shopinvader for PoS
[shopinvader_product_attribute_set](shopinvader_product_attribute_set/) | 14.0.1.0.0 |  | Expose all PIM' Attribute sets with Shopinvader
[shopinvader_product_brand](shopinvader_product_brand/) | 14.0.1.3.1 |  | Shopinvader product Brand
[shopinvader_product_brand_image](shopinvader_product_brand_image/) | 14.0.1.1.0 |  | Shopinvader product Brand Image
[shopinvader_product_brand_tag](shopinvader_product_brand_tag/) | 14.0.1.0.0 |  | Index Product Brand Tags in Shopinvader
[shopinvader_product_manufactured_for](shopinvader_product_manufactured_for/) | 14.0.1.0.0 |  | Manage Product Made Specially For Some Customers
[shopinvader_product_media](shopinvader_product_media/) | 14.0.1.0.0 |  | Index storage media data into external search engine
[shopinvader_product_new](shopinvader_product_new/) | 14.0.1.0.1 |  | Shopinvader product new
[shopinvader_product_order](shopinvader_product_order/) | 14.0.1.0.0 |  | Manage product display order on Shopinvader
[shopinvader_product_price_tax](shopinvader_product_price_tax/) | 14.0.1.1.0 |  | Exposes product prices with and without taxes
[shopinvader_product_stock](shopinvader_product_stock/) | 14.0.1.0.1 |  | This module is used to choose a stock field during theexport (by backend)
[shopinvader_product_stock_assortment](shopinvader_product_stock_assortment/) | 14.0.1.0.1 |  | This module is used to let the Shopinvader product assortment use the stock context in Shopinvader product stock.
[shopinvader_product_stock_state](shopinvader_product_stock_state/) | 14.0.1.0.0 |  | This module is used to choose a stock state during theexport (by backend)
[shopinvader_product_template_multi_link](shopinvader_product_template_multi_link/) | 14.0.1.1.0 |  | Shopinvader Product Link
[shopinvader_product_template_multi_link_date_span](shopinvader_product_template_multi_link_date_span/) | 14.0.1.0.0 |  | Integrate `product_template_multi_link_date_span` in Shopinvader
[shopinvader_product_template_tags](shopinvader_product_template_tags/) | 14.0.1.0.0 |  | Index Product Template Tags in Shopinvader
[shopinvader_product_variant_multi_link](shopinvader_product_variant_multi_link/) | 14.0.1.0.0 |  | Integrate product_variant_multi_link with Shopinvader
[shopinvader_product_variant_selector](shopinvader_product_variant_selector/) | 14.0.1.0.0 |  | Ease creation of variants selector on shopinvader sites
[shopinvader_quotation](shopinvader_quotation/) | 14.0.2.2.1 |  | Shopinvader Quotation
[shopinvader_sale_amount_by_group](shopinvader_sale_amount_by_group/) | 14.0.1.0.0 |  | Expose the amount by tax to shopinvader
[shopinvader_sale_coupon](shopinvader_sale_coupon/) | 14.0.1.0.1 |  | Manage Promotion and Coupon programs in Shopinvader
[shopinvader_sale_packaging](shopinvader_sale_packaging/) | 14.0.1.0.0 |  | Shopinvader Sale Packaging
[shopinvader_sale_packaging_wishlist](shopinvader_sale_packaging_wishlist/) | 14.0.1.0.0 |  | Add packaging information to wishlists
[shopinvader_sale_profile](shopinvader_sale_profile/) | 14.0.1.2.0 |  | ShopInvader - Sale profile
[shopinvader_search_engine](shopinvader_search_engine/) | 14.0.1.3.2 |  | Shopinvader Catalog Search Engine Connector
[shopinvader_wishlist](shopinvader_wishlist/) | 14.0.1.0.0 |  | Handle shop wishlist


Unported addons
---------------
addon | version | maintainers | summary
--- | --- | --- | ---
[partner_contact_company](partner_contact_company/) | 10.0.1.0.0 (unported) |  | Partner Company
[product_online_category](product_online_category/) | 10.0.1.0.0 (unported) |  | Product categories dedicated to online shop
[shopinvader_contact_company](shopinvader_contact_company/) | 10.0.1.0.0 (unported) |  | Make available the field company in the address form
[shopinvader_delivery_instruction](shopinvader_delivery_instruction/) | 13.0.1.0.0 (unported) |  | Shopinvader addons to let user define delivery instructions
[shopinvader_demo_app](shopinvader_demo_app/) | 12.0.2.0.4 (unported) |  | Shopinvader Demo App
[shopinvader_locomotive_contact_company](shopinvader_locomotive_contact_company/) | 10.0.1.0.0 (unported) |  | Synchronize the contact_name with customer name
[shopinvader_locomotive_elasticsearch](shopinvader_locomotive_elasticsearch/) | 12.0.1.1.0 (unported) |  | This addons is used to push the initial elasticsearch configuration to locomotive
[shopinvader_promotion_rule](shopinvader_promotion_rule/) | 10.0.1.0.0 (unported) |  | Module to manage Promotion Rule with shopinvader
[shopinvader_sale_communication](shopinvader_sale_communication/) | 10.0.1.0.0 (unported) |  | This module adds information fields for customers and vendors.
[shopinvader_sale_report](shopinvader_sale_report/) | 10.0.1.0.0 (unported) |  | Shopinvader addons to extend sale report with backend

[//]: # (end addons)
