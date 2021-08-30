# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader Customer Autobind",
    "summary": """
        Allows to autobind new customers (Odoo) to Shopinvader backends""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "depends": ["shopinvader", "web_notify"],
    "data": ["views/shopinvader_backend.xml"],
    "demo": ["demo/mail_template.xml"],
}
