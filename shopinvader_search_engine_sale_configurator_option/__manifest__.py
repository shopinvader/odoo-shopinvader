# Copyright 2021 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader Search Engine Sale Configurator Option",
    "summary": "Index sale configurator option into external search engine",
    "version": "14.0.1.0.0",
    "category": "e-commerce",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "author": "Akretion",
    "license": "AGPL-3",
    "installable": True,
    "auto_install": True,
    "depends": ["shopinvader", "sale_configurator_option"],
    "data": ["data/ir_product_export.xml"],
    "auto_install": True,
}
