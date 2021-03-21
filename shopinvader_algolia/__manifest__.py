# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


{
    "name": "Shopinvader Algolia Connector",
    "version": "10.0.1.0.0",
    "author": "Akretion",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "license": "AGPL-3",
    "category": "Generic Modules",
    "post_init_hook": "post_init_hook",
    "depends": ["shopinvader_search_engine", "connector_algolia"],
    "data": ["data/ir_export_product.xml"],
    "demo": ["demo/backend_demo.xml", "demo/product_demo.xml"],
    "installable": True,
    "application": True,
}
