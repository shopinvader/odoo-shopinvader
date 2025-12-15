# Copyright 2025 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader API Warehouse Sale Channel",
    "version": "16.0.1.0.0",
    "author": "Akretion, Odoo Community Association (OCA)",
    "summary": "Glue module to use Shopinvader API Warehouse with Sale Channel",
    "category": "Uncategorized",
    "depends": [
        "shopinvader_api_warehouse",
        "shopinvader_sale_channel",
    ],
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "data": [
        "views/stock_warehouse_views.xml",
    ],
    "maintainers": ["paradoxxxzero"],
    "demo": [],
    "installable": True,
    "license": "AGPL-3",
    "auto_install": True,
}
