# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from typing import Annotated

from fastapi import APIRouter, Depends

from odoo import api

from odoo.addons.fastapi.dependencies import odoo_env
from odoo.addons.shopinvader_router_helper import VirtualModel

from ..schemas import Lead, LeadInput

lead_router = APIRouter(tags=["leads"])


class LeadHelper(VirtualModel):
    _inherit = "shopinvader.router.helper"
    _name = "shopinvader_api_lead.routers.helper"
    _description = "Shopinvader API Lead Router Helper"

    _model = "crm.lead"

    def _domain(self):
        return []


def lead_helper(
    env: Annotated[api.Environment, Depends(odoo_env)],
):
    return env["shopinvader_api_lead.routers.helper"].new()


@lead_router.post("/leads", status_code=201)
def create(
    data: LeadInput,
    helper: Annotated[LeadHelper, Depends(lead_helper)],
) -> Lead | None:
    lead = helper.create(data.to_crm_lead_vals())
    return Lead.from_crm_lead(lead)
