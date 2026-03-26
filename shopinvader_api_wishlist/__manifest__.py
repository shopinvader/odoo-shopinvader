# Copyright 2019 Camptocamp SA
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader Wishlist",
    "summary": "Handle shop wishlist",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV, Camptocamp,Odoo Community Association (OCA)",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "depends": [
        "sale_wishlist",
        "extendable_fastapi",
        "shopinvader_router_helper",
        "shopinvader_api_security_sale",
        "shopinvader_schema_sale",
        "shopinvader_sale_cart",
    ],
    "data": [
        "security/groups.xml",
        "security/acl_sale_product_set_wizard.xml",
        "security/rule+acl_product_set.xml",
        "security/rule+acl_product_set_line.xml",
    ],
    "installable": True,
}
