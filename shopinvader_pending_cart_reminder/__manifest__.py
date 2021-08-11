# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Shopinvader pending cart reminder",
    "summary": """Shopinvader module to relaunch the customer when the
    cart/sale is not confirmed yet.
    Configure the delay and the email template on the backend.""",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "category": "e-commerce",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "depends": ["shopinvader"],
    "data": [
        "data/ir_cron.xml",
        "data/mail_template.xml",
        "views/shopinvader_backend.xml",
    ],
    "installable": True,
}
