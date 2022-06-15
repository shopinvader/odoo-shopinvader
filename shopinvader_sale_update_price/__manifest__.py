# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader Sale Update Price",
    "summary": """
        Triggers the sale order price computation in case of pricelist change""",
    "version": "13.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "depends": ["shopinvader", "sale_order_price_recalculation"],
    "data": ["views/shopinvader_backend.xml"],
}
