# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader Sale Communication",
    "summary": """
        This module adds information fields for customers and vendors.""",
    "version": "13.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "depends": ["sale", "shopinvader"],
    "data": [
        "security/ir.model.access.csv",
        "views/sale_order.xml",
        "views/sale_communication.xml",
    ],
    "demo": [],
    "installable": True,
    "application": False,
}
