# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductCategory(models.Model):
    _inherit = "product.category"

    shopinvader_bind_ids = fields.One2many(
        "shopinvader.category",
        "record_id",
        string="Shopinvader Binding",
        context={"active_test": False},
    )
    filter_ids = fields.Many2many(
        comodel_name="product.filter", string="Filter"
    )
    active = fields.Boolean(default=True, inverse="_inverse_active")

    @api.multi
    def _inverse_active(self):
        categories = self.filtered(lambda p: not p.active)
        categories = categories.with_prefetch(self._prefetch)
        categories.mapped("shopinvader_bind_ids").write({"active": False})
