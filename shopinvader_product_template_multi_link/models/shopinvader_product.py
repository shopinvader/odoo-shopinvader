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
        current_backend = self.backend_id
        # Get links of the given link_type
        product_links = self.product_template_link_ids.filtered(
            lambda x: x.type_id.code == link_type
        )
        # Get bindings
        shop_binds = product_links.mapped(
            "left_product_tmpl_id.shopinvader_bind_ids"
        )
        shop_binds |= product_links.mapped(
            "right_product_tmpl_id.shopinvader_bind_ids"
        )
        # Get bindings related to current backend and current lang
        lang_binds = shop_binds.filtered(
            lambda b: b.backend_id == current_backend
            and b.lang_id == self.lang_id
        )
        # Get man variant
        variants = self.env["shopinvader.variant"].browse()
        for lang_bind in lang_binds:
            variants |= fields.first(
                lang_bind.shopinvader_variant_ids.filtered(lambda v: v.main)
            )
        return variants

    @api.multi
    def _compute_shopinvader_link(self):
        for record in self:
            record.cross_selling_ids = record._get_shopinvader_variant_link(
                "cross-selling"
            )
            record.up_selling_ids = record._get_shopinvader_variant_link(
                "up_sell"
            )
