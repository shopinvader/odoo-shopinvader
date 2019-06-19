# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader Account Cross Border",
    "summary": """
        Allows to manage the good fiscal position for
        cross border deliveries""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "depends": ["shopinvader", "account"],
    "data": [
        "security/shopinvader_tax_mapping.xml",
        "views/shopinvader_backend.xml",
    ],
}
