# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from typing import List

from fastapi import APIRouter

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.addons.fastapi.depends import (
    authenticated_partner,
    authenticated_partner_from_basic_auth_user,
    authenticated_partner_impl,
    fastapi_endpoint,
    odoo_env,
)

class FastapiEndpoint(models.Model):

    _inherit = "fastapi.endpoint"

    app: str = fields.Selection(
        selection_add=[("shopinvader_demo", "Shopinvader Demo Endpoint")],
        ondelete={"shopinvader_demo": "cascade"},
    )

    shopinvader_demo_auth_method = fields.Selection(
        selection=[("http_basic", "HTTP Basic")],
        string="Authenciation method",
    )

    @api.model
    def _get_fastapi_routers(self):
        if self.app == "shopinvader_demo":
            return self._get_shopinvader_demo_fastapi_routers()
        return super().get_fastapi_routers()

    @api.model
    def _get_shopinvader_demo_fastapi_routers(self) -> List[APIRouter]:
        return []

    @api.constrains("app", "shopinvader_demo_auth_method")
    def _valdiate_demo_auth_method(self):
        for rec in self:
            if rec.app == "shopinvader_demo" and not rec.shopinvader_demo_auth_method:
                raise ValidationError(
                    _(
                        "The authentication method is required for app %(app)s",
                        app=rec.app,
                    )
                )
    
    @api.model
    def _fastapi_app_fields(self) -> List[str]:
        fields = super()._fastapi_app_fields()
        fields.append("shopinvader_demo_auth_method")
        return fields
    
    def _get_app(self):
        app = super()._get_app()
        if self.app == "shopinvader_demo_auth_method":
            # Here we add the overrides to the authenticated_partner_impl method
            # according to the authentication method configured on the demo app
            if self.demo_auth_method == "http_basic":
                authenticated_partner_impl_override = (
                    authenticated_partner_from_basic_auth_user
                )
            app.dependency_overrides[
                authenticated_partner_impl
            ] = authenticated_partner_impl_override
        return app