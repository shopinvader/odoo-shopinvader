from typing import Annotated
from fastapi import APIRouter, Depends

from odoo.addons.base.models.res_partner import Partner as ResPartner
from odoo.api import Environment
from odoo.addons.fastapi.dependencies import odoo_env, authenticated_partner

from ..schemas import LeadService


# create a router
leads_router = APIRouter()


@leads_router.post(
    "/leads",
    status_code=201
)
def post_leads(
    data: LeadService,
    env: Annotated[Environment, Depends(odoo_env)],
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
) -> None:
    env['crm.lead'].create(data.to_crm_lead_vals(partner))
