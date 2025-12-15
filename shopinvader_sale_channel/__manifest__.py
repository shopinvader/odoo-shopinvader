# Copyright 2025 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader Sale Channel",
    "version": "16.0.1.0.0",
    "author": "Akretion, Odoo Community Association (OCA)",
    "summary": "Adds sale channel management to Shopinvader",
    "category": "Uncategorized",
    "depends": [
        "fastapi_endpoint_context",
        "sale_channel",
    ],
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "data": [
        "views/fastapi_endpoint_views.xml",
    ],
    "maintainers": ["paradoxxxzero"],
    "demo": [],
    "installable": True,
    "license": "AGPL-3",
}
