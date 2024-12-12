# Copyright 2023 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


import logging
import sys

from fastapi import Depends, HTTPException, Request, Response, status

from odoo.api import Environment

from odoo.addons.base.models.res_partner import Partner
from odoo.addons.fastapi.dependencies import odoo_env
from odoo.addons.fastapi_auth_partner.dependencies import (
    auth_partner_optionally_authenticated_partner,
)

if sys.version_info >= (3, 9):
    from typing import Annotated
else:
    from typing_extensions import Annotated

_logger = logging.getLogger(__name__)


def auth_partner_authenticated_or_anonymous_partner(
    partner: Annotated[
        Partner,
        Depends(auth_partner_optionally_authenticated_partner),
    ],
    env: Annotated[Environment, Depends(odoo_env)],
    request: Request,
) -> Partner:
    if partner:
        return partner
    anonymous_partner = env["res.partner"]._get_anonymous_partner__cookie(
        request.cookies
    )
    if anonymous_partner:
        return env["res.partner"].browse(anonymous_partner.id)
    _logger.info(
        "Partner auth authentication failed and no anonymous partner cookie found."
    )
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


def auth_partner_authenticated_or_anonymous_partner_autocreate(
    partner: Annotated[
        Partner,
        Depends(auth_partner_optionally_authenticated_partner),
    ],
    env: Annotated[Environment, Depends(odoo_env)],
    request: Request,
    response: Response,
) -> Partner:
    if partner:
        return partner
    anonymous_partner = env["res.partner"]._get_anonymous_partner__cookie(
        request.cookies
    )
    if not anonymous_partner:
        anonymous_partner = env["res.partner"]._create_anonymous_partner__cookie(
            response
        )
    return env["res.partner"].browse(anonymous_partner.id)
