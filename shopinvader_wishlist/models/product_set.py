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

    def get_line_by_product(self, product_id=None, invader_variant_id=None):
        # Backward compat
        _logger.info(
            "DEPRECATED `get_line_by_product`. Use `get_lines_by_products`"
        )
        if product_id:
            product_id = [product_id]
        if invader_variant_id:
            invader_variant_id = [invader_variant_id]
        return self.get_lines_by_products(
            product_ids=product_id, invader_variant_ids=invader_variant_id
        )

    def get_lines_by_products(
        self, product_ids=None, invader_variant_ids=None
    ):
        if not product_ids and not invader_variant_ids:
            raise exceptions.ValidationError(
                _("Provide `product_ids` or `invader_variant_id`")
            )
        if product_ids:
            return self.set_line_ids.filtered(
                lambda x: x.product_id.id in product_ids
            )
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
        for record in self:
            if record.product_id and not record.shopinvader_variant_id:
                backend = record.product_set_id.shopinvader_backend_id
                lang = self.env.context.get("lang")
                variant = record.product_id._get_invader_variant(backend, lang)
                if not variant:
                    lang = record.product_set_id.partner_id.lang
                    # try w/ partner lang
                    variant = record.product_id._get_invader_variant(
                        backend, lang
                    )
                record.shopinvader_variant_id = variant
