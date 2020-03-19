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
    def _get_shopinvader_variant_link(self, link_type):
        self.ensure_one()
        res = []
        current_backend = self.backend_id
        # Get links of the given link_type
        for link in self.product_template_link_ids.filtered(
            lambda x: x.link_type == link_type
        ):
            bindings = link.linked_product_template_id.shopinvader_bind_ids
            for binding in bindings:
                # Get bindings of the correct backend and lang
                if (
                    binding.backend_id == current_backend
                    and binding.lang_id == self.lang_id
                ):
                    # Set only the "main" shopinvader variant
                    for shopinvader_variant in binding.shopinvader_variant_ids:
                        if shopinvader_variant.main:
                            res.append(shopinvader_variant.id)
                            break
        return res

    @api.multi
    def _compute_shopinvader_link(self):
        for record in self:
            record.cross_selling_ids = record._get_shopinvader_variant_link(
                "cross_sell"
            )
            record.up_selling_ids = record._get_shopinvader_variant_link(
                "up_sell"
            )
