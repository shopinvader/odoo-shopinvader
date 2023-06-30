# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader API Cart",
    "summary": """
        Cart FastAPI designed to work with the shopinvader-js-cart library
        see (https://github.com/shopinvader/shopinvader-js-cart)""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "depends": [
        "sale",
        "sale_cart",
        "sale_discount_display_amount",
        "onchange_helper",
        "pydantic",
        "extendable",
        "fastapi",
        "extendable_fastapi",
        "shopinvader_sale_cart",
        "shopinvader_schema_address",
    ],
    "data": [
        "security/groups.xml",
        "security/acl_ir_sequence.xml",
        "security/acl_product_product.xml",
        "security/acl_product_template.xml",
        "security/acl_uom_uom.xml",
        "security/rule+acl_sale_order.xml",
        "security/rule+acl_sale_order_line.xml",
    ],
    "demo": [],
    "external_dependencies": {
        "python": [
            "fastapi",
            "pydantic",
            "extendable-pydantic",
        ]
    },
    "pre_init_hook": "pre_init_hook",
}
