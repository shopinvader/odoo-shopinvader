# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import _, api, exceptions, fields, models

_logger = logging.getLogger(__name__)


class ProductSet(models.Model):

    _inherit = "product.set"

    shopinvader_backend_id = fields.Many2one(
        comodel_name="shopinvader.backend",
        help="If you are using this set for shopinvader customer "
        "you must select a backend.",
    )

    def get_lines_by_products(self, product_ids=None, invader_variant_ids=None):
        if not product_ids and not invader_variant_ids:
            raise exceptions.ValidationError(
                _("Provide `product_ids` or `invader_variant_id`")
            )
        if product_ids:
            return self.set_line_ids.filtered(lambda x: x.product_id.id in product_ids)
        else:
            return self.set_line_ids.filtered(
                lambda x: x.shopinvader_variant_id.id in invader_variant_ids
            )


class ProductSetLine(models.Model):

    _inherit = "product.set.line"

    shopinvader_variant_id = fields.Many2one(
        comodel_name="shopinvader.variant",
        compute="_compute_shopinvader_variant",
        inverse="_inverse_shopinvader_variant",
    )

    def _inverse_shopinvader_variant(self):
        for record in self:
            if record.shopinvader_variant_id and not record.product_id:
                record.product_id = record.shopinvader_variant_id.record_id

    @api.depends("product_id")
    @api.depends_context("lang")
    def _compute_shopinvader_variant(self):
        # Load inactive records too
        # because it's not granted that the product has an active variant.
        for record in self.with_context(active_test=False):
            backend = record.product_set_id.shopinvader_backend_id
            lang = self.env.context.get("lang")
            variant = record.product_id._get_invader_variant(backend, lang)
            if not variant:
                lang = record.product_set_id.partner_id.lang
                # try w/ partner lang
                variant = record.product_id._get_invader_variant(backend, lang)
            if len(variant) > 1:
                # Pick the 1st active variant if any.
                # If there's only an inactive variant
                # the wishlist service is already safe
                # as it will return the product as not available.
                # See `_json_parser_binding_not_available_data`.
                # However, if there's at least an active variant, let's use it.
                active_variant = variant.filtered(lambda x: x.active)
                variant = fields.first(active_variant) if active_variant else variant[0]
            record.shopinvader_variant_id = variant
