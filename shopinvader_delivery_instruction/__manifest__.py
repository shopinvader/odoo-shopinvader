# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Shopinvader delivery instruction",
    "summary": """Shopinvader addons to let user define delivery
    instructions""",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "category": "e-commerce",
    "version": "14.0.1.0.1",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "shopinvader",
        # OCA/sale-workflow
        "sale_stock_picking_note",
    ],
}
