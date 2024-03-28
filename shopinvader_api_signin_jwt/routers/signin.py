# Copyright 2023 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging
from typing import Annotated, Union

from fastapi import APIRouter, Depends, Response, status

from odoo import api, models

from odoo.addons.base.models.res_partner import Partner
from odoo.addons.fastapi.dependencies import odoo_env
from odoo.addons.fastapi_auth_jwt.dependencies import (
    Payload,
    auth_jwt_authenticated_payload,
    auth_jwt_default_validator_name,
    auth_jwt_optionally_authenticated_partner,
)

_logger = logging.getLogger(__name__)

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


@signin_router.post("/signout")
def signout(
    env: Annotated[api.Environment, Depends(odoo_env)],
    default_validator_name: Annotated[
        Union[str, None], Depends(auth_jwt_default_validator_name)
    ],
    response: Response,
) -> None:
    """
    Remove the session cookie.
    """
    validator = (
        env["auth.jwt.validator"].sudo()._get_validator_by_name(default_validator_name)
    )
    if not validator:
        _logger.info("No validator found with name '%s'", default_validator_name)
        return
    if not validator.cookie_name:
        _logger.info("Cookie name not set for validator %s", validator.name)
        return
    response.delete_cookie(
        key=validator.cookie_name,
        path=validator.cookie_path or "/",
        secure=validator.cookie_secure,
        httponly=True,
    )


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
