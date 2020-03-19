# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Shopinvader cart expiry",
    "summary": """Shopinvader module to manage an expiry delay on cart""",
    "author": "ACSONE SA/NV",
    "website": "http://www.shopinvader.com",
    "category": "e-commerce",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "depends": ["shopinvader", "queue_job"],
    "data": ["data/ir_cron.xml", "views/shopinvader_backend.xml"],
}
