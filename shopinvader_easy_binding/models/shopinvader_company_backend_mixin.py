# Copyright 2021 Camptocamp (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ShopinvaderCompanyBackendMixin(models.AbstractModel):
    _name = "shopinvader.company.backend.mixin"
    _description = "Shopinvader Company Backend Mixin"

    shopinvader_company_backend_id = fields.Many2one(
        "shopinvader.backend",
        string="Company Shopinvader Backend",
        help="Technical field: The company's main shopinvader backend.",
        compute="_compute_shopinvader_company_backend_id",
        compute_sudo=True,
    )

    @api.model
    def _get_shopinvader_company_backend(self):
        return self.env.company.shopinvader_company_backend_id

    @api.model
    def _ensure_shopinvader_company_backend(self):
        backend = self._get_shopinvader_company_backend()
        if not backend:
            raise UserError(
                _(
                    "You need to configure a Shopinvader backend for company '%s'.\n"
                    "To do so, go to Shopinvader > Settings.",
                    self.env.company.name,
                )
            )
        return backend

    @api.model
    def _get_shopinvader_company_binding_domain(self):
        backend = self._get_shopinvader_company_backend()
        return [("backend_id", "=", backend.id)]

    @api.depends("company_id")
    @api.depends_context("company")
    def _compute_shopinvader_company_backend_id(self):
        self.shopinvader_company_backend_id = self._get_shopinvader_company_backend()
