# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader Cart",
    "summary": """
        ShopInvader logic for sale carts.""",
    "version": "16.0.1.0.1",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "depends": [
        "sale",
        "onchange_helper",
    ],
    "data": [
        "views/sale_order.xml",
    ],
}
