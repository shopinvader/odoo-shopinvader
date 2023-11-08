# Copyright 2023 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader Schema Sale",
    "summary": "Add schema sale",
    "version": "16.0.1.0.0",
    "development_status": "Alpha",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "author": " Akretion",
    "license": "AGPL-3",
    "depends": [
        "sale_cart",
        "sale_discount_display_amount",
        "shopinvader_schema_address",
    ],
    "external_dependencies": {
        "python": ["extendable_pydantic>=1.2.0", "pydantic>=2.0.0"]
    },
    "data": [],
    "demo": [],
}
