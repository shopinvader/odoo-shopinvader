# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader Sale Cart Delivery",
    "summary": """
        Shopinvader: Manage delivery on sale_cart""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "depends": [
        "sale_cart_delivery_rest_api",
        "shopinvader_sale_cart",
        "shopinvader_delivery_carrier",
    ],
    "data": ["views/shopinvader_backend.xml"],
    "demo": [],
}
