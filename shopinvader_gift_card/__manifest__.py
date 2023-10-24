# Copyright 2021 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "shopinvader_gift_card",
    "summary": "Shopinvader Services for Gift Cards",
    "version": "14.0.1.0.0",
    "category": "e-commerce",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "author": "Akretion, Odoo Community Association (OCA)",
    "maintainers": ["Kev-Roche"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "gift_card",
        "base_rest",
        "base_jsonify",
        "base_rest_datamodel",
        "shopinvader",
    ],
    "demo": [
        "demo/demo.xml",
    ],
    "data": [
        "data/data.xml",
        "views/gift_card.xml",
    ],
}
