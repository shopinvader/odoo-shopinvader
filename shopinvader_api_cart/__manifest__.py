# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader API Cart",
    "summary": """
        Cart FastAPI designed to work with the shopinvader-js-cart library
        see (https://github.com/shopinvader/shopinvader-js-cart)""",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "depends": [
        "shopinvader_router_helper",
        "sale_discount_display_amount",
        "extendable_fastapi",
        "shopinvader_sale_cart",
        "shopinvader_schema_address",
        "shopinvader_schema_sale",
        "shopinvader_api_security_sale",
    ],
    "data": [
        "security/acl_ir_sequence.xml",
    ],
    "installable": True,
}
