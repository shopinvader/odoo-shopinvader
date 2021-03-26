# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Partner Company",
    "version": "10.0.1.0.1",
    "author": "Akretion",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "license": "AGPL-3",
    "category": "Partner",
    "summary": "Partner Company",
    "depends": ["base"],
    "excludes": [
        "partner_firstname"
    ],  # key only known from 12.0 but set for memory
    "data": ["views/partner_view.xml", "views/users_view.xml"],
    "demo": ["demo/partner.xml"],
    "installable": True,
}
