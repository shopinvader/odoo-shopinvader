# Copyright 2024 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader Api Security invoice",
    "summary": "Add security rule to expose invoices",
    "version": "16.0.1.0.0",
    "development_status": "Alpha",
    "category": "Uncategorized",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        "account",
        "fastapi",
    ],
    "data": [
        "security/groups.xml",
        "security/acl_product_product.xml",
        "security/acl_product_template.xml",
        "security/acl_uom_uom.xml",
        "security/rule+acl_account_move.xml",
        "security/rule+acl_account_move_line.xml",
    ],
}
