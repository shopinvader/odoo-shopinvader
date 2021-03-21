# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader Guest Mode",
    "summary": """
        Guest mode for Shopinvader""",
    "version": "10.0.1.0.2",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "depends": ["shopinvader"],
    "data": [
        "data/ir_cron.xml",
        "views/shopinvader_backend.xml",
        "views/shopinvader_partner.xml",
    ],
    "demo": [],
}
