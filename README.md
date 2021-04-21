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
addon | version | summary
--- | --- | ---
[base_url](base_url/) | 13.0.1.1.1 | keep history of url for products & categories
[shopinvader](shopinvader/) | 13.0.6.2.0 | Shopinvader
[shopinvader_algolia](shopinvader_algolia/) | 13.0.1.2.3 | Shopinvader Algolia Connector
[shopinvader_assortment](shopinvader_assortment/) | 13.0.2.0.0 | Shopinvader Assortment
[shopinvader_backend_image_proxy](shopinvader_backend_image_proxy/) | 13.0.1.0.0 | Add possibility to replace the image URL by the proxy url set on the SE backend
[shopinvader_cart_expiry](shopinvader_cart_expiry/) | 13.0.2.0.0 | Shopinvader module to manage an expiry delay on cart
[shopinvader_category_image_for_product](shopinvader_category_image_for_product/) | 13.0.1.0.0 | Shopinvader Display category image for product
[shopinvader_customer_multi_user](shopinvader_customer_multi_user/) | 13.0.2.1.0 | Enable registration of multiple users per each company customer.
[shopinvader_customer_multi_user_wishlist](shopinvader_customer_multi_user_wishlist/) | 13.0.1.0.1 | Integrate customer multi user and wishlist.
[shopinvader_delivery_carrier](shopinvader_delivery_carrier/) | 13.0.3.0.0 | Carrier integration for Shopinvader
[shopinvader_delivery_instruction](shopinvader_delivery_instruction/) | 13.0.1.0.0 | Shopinvader addons to let user define delivery instructions
[shopinvader_elasticsearch](shopinvader_elasticsearch/) | 13.0.1.1.0 | Shopinvader Elasticsearch Connector
[shopinvader_guest_mode](shopinvader_guest_mode/) | 13.0.1.1.0 | Guest mode for Shopinvader
[shopinvader_image](shopinvader_image/) | 13.0.2.0.1 | Add the export of Image for Shopinvader
[shopinvader_import_image](shopinvader_import_image/) | 13.0.3.0.0 | Import product images
[shopinvader_lead](shopinvader_lead/) | 13.0.1.0.1 | Shopinvader Lead Management
[shopinvader_locomotive](shopinvader_locomotive/) | 13.0.3.1.0 | Manage communications between Shopinvader and Locomotive CMS
[shopinvader_locomotive_algolia](shopinvader_locomotive_algolia/) | 13.0.1.0.1 | This addons is used to push the initial algolia configuration to locomotive
[shopinvader_locomotive_guest_mode](shopinvader_locomotive_guest_mode/) | 13.0.1.0.2 | Shopinvader guest mode for locomotive
[shopinvader_locomotive_sale_profile](shopinvader_locomotive_sale_profile/) | 13.0.1.2.0 | Synchronize the sale profile info to customer record on Locomotive
[shopinvader_locomotive_wishlist](shopinvader_locomotive_wishlist/) | 13.0.1.1.0 | Synchronize wishlist details to Locomotive users record.
[shopinvader_notification_default](shopinvader_notification_default/) | 13.0.1.0.0 | Provide default notification templates for Shopinvader suite.
[shopinvader_partner_firstname](shopinvader_partner_firstname/) | 13.0.1.0.0 | Shopinvader Customer firstname/lastname
[shopinvader_product_media](shopinvader_product_media/) | 13.0.1.0.1 | Index storage media data into external search engine
[shopinvader_product_stock](shopinvader_product_stock/) | 13.0.3.0.0 | This module is used to choose a stock field during theexport (by backend)
[shopinvader_product_stock_state](shopinvader_product_stock_state/) | 13.0.1.0.1 | This module is used to choose a stock state during theexport (by backend)
[shopinvader_product_template_multi_link](shopinvader_product_template_multi_link/) | 13.0.2.0.0 | Shopinvader Product Link
[shopinvader_product_template_multi_link_date_span](shopinvader_product_template_multi_link_date_span/) | 13.0.1.0.0 | Integrate `product_template_multi_link_date_span` in Shopinvader
[shopinvader_product_variant_multi_link](shopinvader_product_variant_multi_link/) | 13.0.1.0.2 | Integrate product_variant_multi_link with Shopinvader
[shopinvader_product_variant_selector](shopinvader_product_variant_selector/) | 13.0.1.0.0 | Ease creation of variants selector on shopinvader sites
[shopinvader_sale_packaging](shopinvader_sale_packaging/) | 13.0.2.1.1 | Shopinvader Sale Packaging
[shopinvader_sale_packaging_wishlist](shopinvader_sale_packaging_wishlist/) | 13.0.2.1.1 | Add packaging information to wishlists
[shopinvader_sale_profile](shopinvader_sale_profile/) | 13.0.1.2.0 | ShopInvader - Sale profile
[shopinvader_search_engine](shopinvader_search_engine/) | 13.0.2.0.0 | Shopinvader Catalog Search Engine Connector
[shopinvader_wishlist](shopinvader_wishlist/) | 13.0.3.1.2 | Handle shop wishlist


Unported addons
---------------
addon | version | summary
--- | --- | ---
[partner_contact_company](partner_contact_company/) | 10.0.1.0.0 (unported) | Partner Company
[product_online_category](product_online_category/) | 10.0.1.0.0 (unported) | Product categories dedicated to online shop
[shopinvader_contact_company](shopinvader_contact_company/) | 10.0.1.0.0 (unported) | Make available the field company in the address form
[shopinvader_custom_attribute](shopinvader_custom_attribute/) | 10.0.1.0.0 (unported) | Integrate your custom attribute in your website
[shopinvader_demo_app](shopinvader_demo_app/) | 12.0.2.0.4 (unported) | Shopinvader Demo App
[shopinvader_invoice](shopinvader_invoice/) | 12.0.1.1.1 (unported) | Shopinvader Invoice module
[shopinvader_locomotive_contact_company](shopinvader_locomotive_contact_company/) | 10.0.1.0.0 (unported) | Synchronize the contact_name with customer name
[shopinvader_locomotive_elasticsearch](shopinvader_locomotive_elasticsearch/) | 12.0.1.1.0 (unported) | This addons is used to push the initial elasticsearch configuration to locomotive
[shopinvader_locomotive_reset_password](shopinvader_locomotive_reset_password/) | 10.0.1.0.0 (unported) | Give the possibility to send a email to reset thepassword from odoo
[shopinvader_multi_category](shopinvader_multi_category/) | 10.0.1.0.0 (unported) | Shopinvader Many Categories
[shopinvader_partner_vat](shopinvader_partner_vat/) | 12.0.1.0.0 (unported) | Shopinvader Check VAT with invader environnement
[shopinvader_pending_cart_reminder](shopinvader_pending_cart_reminder/) | 12.0.1.0.0 (unported) | Shopinvader module to relaunch the customer when the cart/sale is not confirmed yet. Configure the delay and the email template on the backend.
[shopinvader_product_new](shopinvader_product_new/) | 10.0.0.0.0 (unported) | Shopinvader product new
[shopinvader_product_stock_assortment](shopinvader_product_stock_assortment/) | 13.0.1.0.0 (unported) | This module is used to let the Shopinvader product assortment use the stock context in Shopinvader product stock.
[shopinvader_promotion_rule](shopinvader_promotion_rule/) | 10.0.1.0.0 (unported) | Module to manage Promotion Rule with shopinvader
[shopinvader_quotation](shopinvader_quotation/) | 12.0.2.0.0 (unported) | Shopinvader Quotation
[shopinvader_sale_communication](shopinvader_sale_communication/) | 10.0.1.0.0 (unported) | This module adds information fields for customers and vendors.
[shopinvader_sale_report](shopinvader_sale_report/) | 10.0.1.0.0 (unported) | Shopinvader addons to extend sale report with backend

[//]: # (end addons)
