# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Shopinvader Product Stock State",
    "summary": "This module is used to choose a stock state during the"
    "export (by backend)",
    "version": "10.0.1.0.0",
    "category": "e-commerce",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "author": "Akretion",
    "license": "AGPL-3",
    "installable": True,
    "depends": ["product_stock_state", "shopinvader_product_stock"],
    "data": ["views/shopinvader_backend.xml"],
    "external_dependencies": {},
}
