# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader Reset Password",
    "summary": "Give the possibility to send a email to reset the" "password from odoo",
    "version": "14.0.1.0.1",
    "category": "Shopinvader",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "author": " Akretion",
    "license": "AGPL-3",
    "installable": True,
    "depends": ["shopinvader_locomotive"],
    "data": [
        "security/ir_model_access.xml",
        "views/shopinvader_backend.xml",
        "wizards/reset_password_view.xml",
        "views/partner_view.xml",
        "data/mail_template.xml",
        "data/ir_cron.xml",
        "data/queue_job_function_data.xml",
    ],
    "demo": ["demo/shopinvader_backend.xml"],
}
