# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com)
# Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import SUPERUSER_ID
from odoo.api import Environment


def post_init_hook(cr, registry):
    env = Environment(cr, SUPERUSER_ID, {})
    module_obj = env["ir.module.module"]
    product_obj = env["product.template"]
    module = module_obj.search([("name", "=", "shopinvader_algolia")])
    if module.demo:
        product = env.ref("product.product_product_4_product_template")
        description = product.description
        vals = {"description": description}
        products = product_obj.search([])
        products.write(vals)
