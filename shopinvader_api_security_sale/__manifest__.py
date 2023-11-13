# Copyright 2023 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader Api Security Sale",
    "summary": "Add security rule to expose sale order",
    "version": "16.0.1.1.1",
    "development_status": "Alpha",
    "category": "Uncategorized",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "author": " Akretion",
    "license": "AGPL-3",
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "sale",
        "fastapi",
    ],
    "data": [
        "security/groups.xml",
        "security/acl_product_product.xml",
        "security/acl_product_template.xml",
        "security/acl_uom_uom.xml",
        "security/rule+acl_sale_order.xml",
        "security/rule+acl_sale_order_line.xml",
    ],
    "demo": [],
}
