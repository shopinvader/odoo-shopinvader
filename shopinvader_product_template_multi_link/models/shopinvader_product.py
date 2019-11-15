# Copyright 2017 Akretion (http://www.akretion.com).
# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


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

    def _get_linked_shopinvader_variants(self, link_type):
        self.ensure_one()
        res = self.env["shopinvader.variant"].browse()
        current_backend = self.backend_id
        # Get links for the given link_type
        for link in self.product_template_link_ids.filtered(
            lambda x: x.type_id == link_type
        ):
            origin = self.record_id
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
                            res |= shopinvader_variant
                            break
        return res

    def _compute_shopinvader_link(self):
        for record in self:
            record.cross_selling_ids = record._get_linked_shopinvader_variants(
                self.env.ref(
                    "product_template_multi_link."
                    "product_template_link_type_cross_selling"
                )
            )
            record.up_selling_ids = record._get_linked_shopinvader_variants(
                self.env.ref(
                    "product_template_multi_link."
                    "product_template_link_type_up_selling"
                )
            )
