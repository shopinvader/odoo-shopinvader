# Copyright 2023 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from typing import Annotated

from fastapi import APIRouter, Depends, Response, status

from odoo import api, models

from odoo.addons.base.models.res_partner import Partner
from odoo.addons.fastapi.dependencies import odoo_env
from odoo.addons.fastapi_auth_jwt.dependencies import (
    Payload,
    auth_jwt_authenticated_payload,
    auth_jwt_optionally_authenticated_partner,
)

signin_router = APIRouter(tags=["signin"])


@signin_router.post("/signin", status_code=200)
def signin(
    env: Annotated[api.Environment, Depends(odoo_env)],
    partner: Annotated[Partner, Depends(auth_jwt_optionally_authenticated_partner)],
    payload: Annotated[Payload, Depends(auth_jwt_authenticated_payload)],
    response: Response,
) -> None:
    """
    Authenticate the partner based on a JWT token or a session cookie.
    Set the session cookie if allowed.
    Return HTTP code 201 if res.partner created (case of the first signin).
    """
    if not partner:
        env[
            "shopinvader_api_signin_jwt.signin_router.helper"
        ]._create_partner_from_payload(payload)
        response.status_code = status.HTTP_201_CREATED


class ShopinvaderApSigninJwtRouterHelper(models.AbstractModel):
    _name = "shopinvader_api_signin_jwt.signin_router.helper"
    _description = "ShopInvader API Signin Jwt Router Helper"

    @api.model
    def _get_partner_create_vals(self, payload: Payload):
        return {"name": payload.get("name"), "email": payload.get("email")}

    @api.model
    def _create_partner_from_payload(self, payload: Payload):
        partner = (
            self.env["res.partner"]
            .sudo()
            .create(self._get_partner_create_vals(payload))
        )
        return self.env["res.partner"].browse(partner.id)
