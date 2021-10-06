# Copyright 2021 Camptocamp (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductProduct(models.Model):
    _name = "product.product"
    _inherit = ["product.product", "shopinvader.company.backend.mixin"]

    # Warning: These fields are only intended to be used from the UI.
    # Result will not be what you expect if used with with_company,
    # due to their cache not being invalidated.

    company_shopinvader_bind_ids = fields.One2many(
        "shopinvader.variant",
        "record_id",
        domain=lambda self: self._get_shopinvader_company_binding_domain(),
        readonly=True,
    )
    company_shopinvader_published = fields.Boolean(
        string="Published on Shopinvader",
        compute="_compute_company_shopinvader_published",
        inverse="_inverse_company_shopinvader_published",
        search="_search_company_shopinvader_published",
    )

    @api.depends("company_shopinvader_bind_ids.active")
    def _compute_company_shopinvader_published(self):
        for rec in self:
            rec.company_shopinvader_published = bool(
                rec.company_shopinvader_bind_ids.filtered("active")
            )

    def _inverse_company_shopinvader_published(self):
        backend = self._ensure_shopinvader_company_backend()
        for rec in self:
            if rec.company_shopinvader_published:
                backend.bind_selected_products(rec, run_immediately=True)
            else:
                rec.company_shopinvader_bind_ids.active = False

    def _search_company_shopinvader_published(self, operator, value):
        if operator not in ("=", "!="):
            raise NotImplementedError()
        if operator == "!=":
            operator = "="
            value = not value
        domain = [("company_shopinvader_bind_ids.active", "=", True)]
        if not value:
            domain = ["!"] + domain
        return domain
