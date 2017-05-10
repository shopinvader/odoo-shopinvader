# -*- coding: utf-8 -*-
# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Shopinvader",
    "summary": "Shopinvader",
    "version": "8.0.1.0.0",
    "category": "e-commerce",
    "website": "https://akretion.com",
    "author": "Akretion",
    "license": "AGPL-3",
    "application": True,
    "installable": True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "base_delivery_carrier_label",
        "base_jsonify",
        "base_sparse_field",
        "base_url",
        "base_view_inheritance_extension",
        "connector_base_product",
        "connector_locomotivecms",
        "connector_nosql_algolia_product",
        "delivery",
        "onchange_helper",
        "payment_gateway",
        "product_media",
        "product_multi_image",
        "product_stock_state",
        "sale_cart",
        "sale_different_invoice_address",
        "sale_payment_method",
        "sale_order_price_recalculation",
        "sale_order_line_price_subtotal_gross",
    ],
    "data": [
        'views/product_view.xml',
        'views/payment_method_view.xml',
        'views/backend_view.xml',
        'views/partner_view.xml',
        'views/product_category_view.xml',
        'views/sale_view.xml',
        'security/ir.model.access.csv',
        "data/res_partner.xml",
        "data/ir_export.xml",
    ],
    "demo": [
        "demo/account_demo.xml",
        "demo/pricelist_demo.xml",
        "demo/backend_demo.xml",
        "demo/partner_demo.xml",
        "demo/sale_demo.xml",
    ],
    "qweb": [
    ]
}
