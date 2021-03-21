# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Shopinvader cart expiry",
    "summary": """Shopinvader module to manage an expiry delay on cart""",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "category": "e-commerce",
    "version": "10.0.1.1.0",
    "license": "AGPL-3",
    "depends": ["shopinvader", "queue_job"],
    "data": ["data/ir_cron.xml", "views/shopinvader_backend.xml"],
}
