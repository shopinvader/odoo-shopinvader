# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Cart Rest Api",
    "summary": """
        Cart REST API designed to work with the shopinvader-js-cart library
        see (https://github.com/shopinvader/shopinvader-js-cart)""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "depends": [
        "base_jsonify",
        "base_rest",
        "partner_serializer",
        "sale_cart",
        "sale_discount_display_amount",
        "onchange_helper",
    ],
    "data": ["views/sale_order.xml"],
    "demo": [],
}
