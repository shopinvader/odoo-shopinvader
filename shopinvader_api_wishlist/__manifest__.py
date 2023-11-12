# Copyright 2019 Camptocamp SA
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader Wishlist",
    "summary": """
        Handle shop wishlist""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV, Camptocamp,Odoo Community Association (OCA)",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "depends": [
        "fastapi",
        "sale_wishlist",
        "extendable_fastapi",
        "shopinvader_api_security_sale",
        "shopinvader_schema_sale",
        "shopinvader_sale_cart",
        "shopinvader_filtered_model",
    ],
    "demo": [],
    "data": [
        "security/groups.xml",
        "security/acl_product_set_add.xml",
        "security/rule+acl_product_set.xml",
        "security/rule+acl_product_set_line.xml",
    ],
    "installable": True,
}
