# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, exceptions, fields, models


class ProductSet(models.Model):

    _inherit = "product.set"

    shopinvader_backend_id = fields.Many2one(
        comodel_name="shopinvader.backend",
        help="If you are using this set for shopinvader customer "
        "you must select a backend.",
    )
    lang_id = fields.Many2one(
        "res.lang",
        string="Lang",
        default=lambda self: self.env["res.lang"]._lang_get(
            self.env.context.get("lang")
        ),
    )

    def get_line_by_product(self, product_id=None, invader_variant_id=None):
        if not product_id and not invader_variant_id:
            raise exceptions.ValidationError(
                _("Provide `product_id` or `invader_variant_id`")
            )
        if product_id:
            return self.set_line_ids.filtered(
                lambda x: x.product_id.id == product_id
            )
        else:
            return self.set_line_ids.filtered(
                lambda x: x.shopinvader_variant_id.id == invader_variant_id
            )


class ProductSetLine(models.Model):

    _inherit = "product.set.line"

    shopinvader_variant_id = fields.Many2one(
        comodel_name="shopinvader.variant",
        compute="_compute_shopinvader_variant",
        inverse="_inverse_shopinvader_variant",
    )
    product_id = fields.Many2one(
        # make it required in the form
        required=False
    )

    @api.multi
    def _inverse_shopinvader_variant(self):
        for record in self:
            if record.shopinvader_variant_id and not record.product_id:
                record.product_id = record.shopinvader_variant_id.record_id

    @api.depends("product_id", "product_set_id.lang_id")
    def _compute_shopinvader_variant(self):
        for record in self:
            if record.product_id and not record.shopinvader_variant_id:
                backend = record.product_set_id.shopinvader_backend_id
                # lang = record.product_set_id.lang_id.code
                # TMP FIX: apparently the lang is not propagate to the context
                # from the locomotive request
                # and we cannot make sure which lang
                # is going to be used.
                # Let's rely only on the partner until we solve it.
                lang = record.product_set_id.partner_id.lang
                # / FIX
                variant = record.product_id._get_invader_variant(backend, lang)
                # if not variant:
                #     lang = record.product_set_id.partner_id.lang
                #     # try w/ partner lang
                #     variant = record.product_id._get_invader_variant(
                #         backend, lang
                #     )
                record.shopinvader_variant_id = variant
