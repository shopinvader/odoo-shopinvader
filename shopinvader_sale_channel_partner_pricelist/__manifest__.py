# Copyright 2026 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader Sale Channel Partner Pricelist",
    "version": "16.0.1.0.0",
    "author": "Akretion, Odoo Community Association (OCA)",
    "summary": "Add a pricelist on sale channel to affect "
    "to every partner created from this channel",
    "category": "Uncategorized",
    "depends": [
        "shopinvader_sale_channel",
    ],
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "data": [
        "views/sale_channel_views.xml",
    ],
    "maintainers": ["paradoxxxzero"],
    "installable": True,
    "license": "AGPL-3",
}
