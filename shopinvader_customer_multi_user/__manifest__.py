# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader Customer Multi User",
    "summary": """
        Enable registration of multiple users per each company customer.""",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "author": "Camptocamp SA",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "depends": [
        "shopinvader",
        "base_partition",  # v12 only: backports filtered_domain
    ],
    "data": [
        "views/shopinvader_backend.xml",
        "views/partner_view.xml",
        "views/shopinvader_partner_view.xml",
    ],
}
