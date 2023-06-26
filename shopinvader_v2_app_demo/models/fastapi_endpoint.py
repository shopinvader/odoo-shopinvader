# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from functools import partial
from typing import Any, List

from fastapi import APIRouter, FastAPI
from fastapi.security import OAuth2AuthorizationCodeBearer

from odoo import api, fields, models

from odoo.addons.fastapi.dependencies import authenticated_partner_impl
from odoo.addons.fastapi_auth_jwt.dependencies import (
    auth_jwt_default_validator_name,
    auth_jwt_http_header_authorization,
)
from odoo.addons.shopinvader_api_address.routers.address_service import address_router
from odoo.addons.shopinvader_api_cart.routers import cart_router
from odoo.addons.shopinvader_fastapi_auth_jwt.dependencies import (
    auth_jwt_authenticated_or_anonymous_partner,
    auth_jwt_authenticated_or_anonymous_partner_autocreate,
)


class FastapiEndpoint(models.Model):

    _inherit = "fastapi.endpoint"

    app: str = fields.Selection(
        selection_add=[("shopinvader_demo", "Shopinvader Demo Endpoint")],
        ondelete={"shopinvader_demo": "cascade"},
    )
    auth_jwt_validator_id = fields.Many2one("auth.jwt.validator")

    @api.model
    def _get_fastapi_routers(self):
        if self.app == "shopinvader_demo":
            return self._get_shopinvader_demo_fastapi_routers()
        return super().get_fastapi_routers()

    @api.model
    def _get_shopinvader_demo_fastapi_routers(self) -> List[APIRouter]:
        if "address" not in address_router.tags:
            address_router.tags.append("address")
        return [address_router]

    def _get_shopinvader_demo_tags(self, params) -> list:
        tags_metadata = params.get("openapi_tags", []) or []
        tags_metadata.append(
            {
                "name": "addresses",
                "description": "Set of services to manage addresses",
            }
        )
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        tags_metadata.append(
            {
                "name": "cart",
                "description": "Set of services to manage carts",
                "externalDocs": {
                    "description": "Cart services are available under "
                    "a specific authentication mechanism",
                    "url": f"{base_url}{self.root_path}/carts/docs",
                },
            }
        )
        return tags_metadata

    def _prepare_fastapi_app_params(self) -> dict[str, Any]:
        params = super()._prepare_fastapi_app_params()
        if self.app == "shopinvader_demo":
            params["openapi_tags"] = self._get_shopinvader_demo_tags(params)
            params[
                "swagger_ui_oauth2_redirect_url"
            ] = "/shopinvader_demo/docs/oauth2-redirect"
        return params

    def _get_app(self):
        app = super()._get_app()
        if self.app == "shopinvader_demo":
            oauth2_scheme = OAuth2AuthorizationCodeBearer(
                authorizationUrl=(
                    "https://keycloak.demo16.shopinvader.com/"
                    "auth/realms/master/protocol/openid-connect/auth"
                ),
                tokenUrl=(
                    "https://keycloak.demo16.shopinvader.com/"
                    "auth/realms/master/protocol/openid-connect/token"
                ),
                scopes={"openid": "", "email": "", "profile": ""},
                # Don't fail if missing Authorization header, as we look for the cookie too.
                auto_error=False,
            )
            app.dependency_overrides[
                authenticated_partner_impl
            ] = auth_jwt_authenticated_or_anonymous_partner
            app.dependency_overrides[auth_jwt_default_validator_name] = partial(
                lambda a: a, self.auth_jwt_validator_id.name or None
            )
            app.dependency_overrides[auth_jwt_http_header_authorization] = oauth2_scheme
            cart_app = FastAPI()
            cart_app.include_router(cart_router)
            cart_app.dependency_overrides[
                authenticated_partner_impl
            ] = auth_jwt_authenticated_or_anonymous_partner_autocreate
            cart_app.dependency_overrides[auth_jwt_default_validator_name] = partial(
                lambda a: a, self.auth_jwt_validator_id.name or None
            )
            cart_app.dependency_overrides[
                auth_jwt_http_header_authorization
            ] = oauth2_scheme
            app.mount("/carts", cart_app)

        return app
