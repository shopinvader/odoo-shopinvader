# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ShopinvaderProduct(models.Model):
    _inherit = "shopinvader.product"

    cross_selling_ids = fields.Many2many(
        comodel_name="shopinvader.variant",
        multi="shopinvader_link",
        compute="_compute_shopinvader_link",
    )

    up_selling_ids = fields.Many2many(
        comodel_name="shopinvader.variant",
        multi="shopinvader_link",
        compute="_compute_shopinvader_link",
    )

    @api.multi
    def _get_shopinvader_variant_link(self):
        self.ensure_one()
        up_sell = []
        cross_sell = []
        current_backend = self.backend_id
        # Get links of the given link_type
        for link in self.product_template_link_ids:
            bindings = link.linked_product_template_id.shopinvader_bind_ids
            # Get bindings of the correct backend and lang
            bindings = bindings.filtered(
                lambda x: x.backend_id == current_backend
                and x.lang_id == self.lang_id
            )
            for binding in bindings:
                # Set only the "main" shopinvader variant
                variants = binding.shopinvader_variant_ids.filtered(
                    lambda x: x.main
                )
                if link.link_type == "cross_sell":
                    cross_sell.extend(variants.ids)
                else:
                    up_sell.extend(variants.ids)
        return up_sell, cross_sell

    @api.multi
    def _compute_shopinvader_link(self):
        for record in self:
            up_sell, cross_sell = record._get_shopinvader_variant_link()
            record.up_selling_ids = up_sell
            record.cross_selling_ids = cross_sell
