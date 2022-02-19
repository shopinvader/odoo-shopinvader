# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader MailJet",
    "summary": "Send shopinvader email using mailjet API",
    "version": "8.0.1.0.0",
    "category": "mail",
    "website": "https://www.akretion.com",
    "author": " Akretion",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": ["mailjet_rest"],
        "bin": [],
    },
    "depends": [
        "shopinvader",
        "account_invoice_sale_link",
    ],
    "data": [
        "views/email_template_view.xml",
        "views/mail_server_view.xml",
        "views/mail_mail_view.xml",
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
