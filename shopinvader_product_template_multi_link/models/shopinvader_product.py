# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# Copyright (C) 2020 (http://www.camptocamp.com)
# @author Simone Orsi <simahawk@gmail.com>
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
        variant_ids = set()
        current_backend = self.backend_id
        origin = self.record_id
        # Get links for the given link_type
        for link in self.product_template_link_ids:
            if link.type_id != link_type:
                continue
            if link.left_product_tmpl_id != origin:
                target = link.left_product_tmpl_id
            else:
                target = link.right_product_tmpl_id
            bindings = target.shopinvader_bind_ids
            for binding in bindings:
                # Get bindings of the correct backend and lang
                if (
                    binding.backend_id == current_backend
                    and binding.lang_id == self.lang_id
                ):
                    # Set only the "main" shopinvader variant
                    for shopinvader_variant in binding.shopinvader_variant_ids:
                        if shopinvader_variant.main:
                            variant_ids.add(shopinvader_variant.id)
                            break
        return self.env["shopinvader.variant"].browse(variant_ids)

    @api.multi
    def _compute_shopinvader_link(self):
        # TODO: make these configurable on backend
        cross_selling_type = self.env.ref(
            "product_template_multi_link."
            "product_template_link_type_cross_selling",
            raise_if_not_found=False,
        )
        up_selling_type = self.env.ref(
            "product_template_multi_link."
            "product_template_link_type_up_selling",
            raise_if_not_found=False,
        )
        for record in self:
            if cross_selling_type:
                record.cross_selling_ids = record._get_linked_shopinvader_variants(
                    cross_selling_type
                )
            else:
                record.cross_selling_ids = False
            if up_selling_type:
                record.up_selling_ids = record._get_linked_shopinvader_variants(
                    up_selling_type
                )
            else:
                record.up_selling_ids = False
