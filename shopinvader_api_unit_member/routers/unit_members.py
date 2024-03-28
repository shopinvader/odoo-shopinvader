# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from typing import Annotated, List

from fastapi import APIRouter, Depends

from odoo import _
from odoo.exceptions import AccessError

from odoo.addons.base.models.res_partner import Partner as ResPartner
from odoo.addons.fastapi.dependencies import authenticated_partner

from ..schemas import UnitMember, UnitMemberCreate, UnitMemberUpdate

# create a router
unit_member_router = APIRouter(tags=["unit"])


def authenticated_manager(
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
) -> ResPartner:
    if partner.unit_profile != "manager":
        raise AccessError(_("Only a manager can perform this action."))
    return partner


@unit_member_router.get("/unit/members")
async def get_unit_members(
    partner: Annotated[ResPartner, Depends(authenticated_manager)],
) -> List[UnitMember]:
    """
    Get list of unit members
    """
    members = partner._get_shopinvader_unit_members()
    return [UnitMember.from_res_partner(rec) for rec in members]


@unit_member_router.get("/unit/members/{member_id}")
async def get_unit_member(
    partner: Annotated[ResPartner, Depends(authenticated_manager)],
    member_id: int,
) -> UnitMember:
    """
    Get a specific unit member
    """
    member = partner._get_shopinvader_unit_member(member_id)
    return UnitMember.from_res_partner(member)


@unit_member_router.post("/unit/members", status_code=201)
async def create_unit_member(
    data: UnitMemberCreate,
    partner: Annotated[ResPartner, Depends(authenticated_manager)],
) -> UnitMember:
    """
    Create a new unit member (manager or collaborator) as manager
    """
    vals = data.to_res_partner_vals()
    member = partner._create_shopinvader_unit_member(vals)
    return UnitMember.from_res_partner(member)


@unit_member_router.post("/unit/members/{member_id}")
async def update_unit_member(
    data: UnitMemberUpdate,
    partner: Annotated[ResPartner, Depends(authenticated_manager)],
    member_id: int,
) -> UnitMember:
    """
    Update a specific unit member (manager or collaborator) as manager
    """
    vals = data.to_res_partner_vals()
    member = partner._update_shopinvader_unit_member(member_id, vals)
    return UnitMember.from_res_partner(member)


@unit_member_router.delete("/unit/members/{member_id}")
async def delete_unit_member(
    partner: Annotated[ResPartner, Depends(authenticated_manager)],
    member_id: int,
) -> UnitMember:
    """
    Delete a specific unit member (manager or collaborator) as manager
    """
    member = partner._delete_shopinvader_unit_member(member_id)
    return UnitMember.from_res_partner(member)
