# Copyright 2023 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging
from typing import Annotated

from fastapi import Depends, HTTPException, Request, Response, status

from odoo.api import Environment

from odoo.addons.base.models.res_partner import Partner
from odoo.addons.fastapi.dependencies import odoo_env
from odoo.addons.fastapi_auth_jwt.dependencies import (
    Payload,
    auth_jwt_optionally_authenticated_partner,
    auth_jwt_optionally_authenticated_payload,
)

_logger = logging.getLogger(__name__)


def auth_jwt_authenticated_or_anonymous_partner(
    auth_jwt_partner: Annotated[
        Partner,
        Depends(auth_jwt_optionally_authenticated_partner),
    ],
    env: Annotated[Environment, Depends(odoo_env)],
    request: Request,
    response: Response,
) -> Partner:
    anonymous_partner = env["res.partner"]._get_anonymous_partner__cookie(
        request.cookies
    )

    if anonymous_partner and auth_jwt_partner:
        env["res.partner"]._promote_anonymous_partner(
            auth_jwt_partner, request.cookies, response
        )

    if auth_jwt_partner:
        return auth_jwt_partner

    if not anonymous_partner:
        _logger.info("JWT authentication failed and no anonymous partner cookie found.")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    return env["res.partner"].browse(anonymous_partner.id)


def auth_jwt_authenticated_or_anonymous_partner_autocreate(
    auth_jwt_partner: Annotated[
        Partner,
        Depends(auth_jwt_optionally_authenticated_partner),
    ],
    payload: Annotated[
        Payload,
        Depends(auth_jwt_optionally_authenticated_payload),
    ],
    env: Annotated[Environment, Depends(odoo_env)],
    request: Request,
    response: Response,
) -> Partner:
    anonymous_partner = env["res.partner"]._get_anonymous_partner__cookie(
        request.cookies
    )

    if not auth_jwt_partner and not anonymous_partner:
        if payload:
            _logger.info(
                "JWT authentication succeeded but no partner was found. "
                "Not attempting to create an anonymous partner."
            )
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        anonymous_partner = env["res.partner"]._create_anonymous_partner__cookie(
            response
        )

    if anonymous_partner and auth_jwt_partner:
        env["res.partner"]._promote_anonymous_partner(
            auth_jwt_partner, request.cookies, response
        )

    if auth_jwt_partner:
        return auth_jwt_partner

    return env["res.partner"].browse(anonymous_partner.id)
