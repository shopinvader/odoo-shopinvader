# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Shopinvader category image for product",
    "summary": "Shopinvader Display category image for product",
    "version": "10.0.1.0.0",
    "category": "e-commerce",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "shopinvader",
        "shopinvader_search_engine",
        "shopinvader_image",
    ],
    "data": ["data/ir_export.xml"],
    "demo": [],
}
