# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from typing import Annotated

from fastapi import Depends

from odoo.addons.base.models.res_partner import Partner as ResPartner
from odoo.addons.fastapi.dependencies import fastapi_endpoint
from odoo.addons.fastapi.models import FastapiEndpoint
from odoo.addons.shopinvader_api_unit_member.routers import unit_member_router
from odoo.addons.shopinvader_api_unit_member.routers.unit_members import (
    authenticated_manager,
)

from ..schemas import UnitMember


@unit_member_router.post("/unit/members/{member_id}/invite")
async def invite_unit_member(
    partner: Annotated[ResPartner, Depends(authenticated_manager)],
    endpoint: Annotated[FastapiEndpoint, Depends(fastapi_endpoint)],
    member_id: int,
) -> UnitMember:
    """
    Invite a unit member to sign in.
    """
    member = partner._invite_shopinvader_unit_member(member_id, endpoint.directory_id)
    return UnitMember.from_res_partner(member)
