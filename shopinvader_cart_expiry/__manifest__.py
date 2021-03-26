# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Shopinvader cart expiry",
    "summary": """Shopinvader module to manage an expiry delay on cart""",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "category": "e-commerce",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "depends": ["shopinvader"],
    "data": [
        "data/ir_cron.xml",
        "views/shopinvader_backend.xml",
        "data/queue_job_function_data.xml",
    ],
    "installable": True,
}
