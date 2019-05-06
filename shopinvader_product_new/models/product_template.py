# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com)
# Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    new_product = fields.Boolean("New product")

    @api.model
    def compute_new_product(self, limit, extra_domain=None):
        new_products = self.search([("new_product", "=", True)])
        new_products.write({"new_product": False})
        domain = [("shopinvader_bind_ids", "!=", False)]
        if extra_domain is not None:
            domain += extra_domain
        new_products = self.search(
            domain, limit=limit, order="create_date desc"
        )
        new_products.write({"new_product": True})
