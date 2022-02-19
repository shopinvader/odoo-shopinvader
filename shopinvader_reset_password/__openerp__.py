# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader Reset Password",
    "summary": "Give the possibility to send a email to reset the"
               "password from odoo",
    "version": "8.0.1.0.0",
    "category": "Shopinvader",
    "website": "https://www.akretion.com",
    "author": " Akretion",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "shopinvader",
    ],
    "data": [
        "views/partner_view.xml",
        "wizards/reset_password_view.xml",
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
