# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader Customer Multi User",
    "summary": """
        Enable registration of multiple users per each company customer.""",
    "version": "14.0.1.2.0",
    "license": "AGPL-3",
    "author": "Camptocamp SA",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "depends": ["shopinvader"],
    "data": [
        "views/shopinvader_backend.xml",
        "views/partner_view.xml",
        "views/shopinvader_partner_view.xml",
    ],
    "installable": True,
}
