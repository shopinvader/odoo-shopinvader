# Copyright 2024 ACSONE SA/NV,Odoo Community Association (OCA)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader Api Customer",
    "summary": "Adds service to manage shopinvader customer",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA),"
    "Odoo Community Association (OCA)",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "depends": [
        "shopinvader_router_helper",
        "extendable_fastapi",
        # Odoo
        "mail",
        "product",
    ],
    "data": [],
    "installable": True,
}
