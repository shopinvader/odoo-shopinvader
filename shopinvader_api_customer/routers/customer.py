# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from typing import Annotated

from fastapi import APIRouter, Depends

from odoo import api, fields

from odoo.addons.base.models.res_partner import Partner as ResPartner
from odoo.addons.fastapi.dependencies import (
    authenticated_partner,
    authenticated_partner_env,
)
from odoo.addons.shopinvader_router_helper import VirtualModel

from ..schemas.customer import Customer, CustomerUpdate

# create a router
customer_router = APIRouter(tags=["customer"])


class CustomerHelper(VirtualModel):
    _inherit = "shopinvader.router.helper"
    _name = "shopinvader_api_customer.router.helper"
    _description = "API Customer Router Helper"
    _model = "res.partner"

    partner = fields.Many2one(
        comodel_name="res.partner",
    )

    def _domain(self):
        return []

    def _get_customer(self) -> ResPartner:
        self.ensure_one()
        return self.get(self.partner.id)

    def _update_shopinvader_customer(self, data: CustomerUpdate) -> ResPartner:
        self.ensure_one()
        values = self._get_shopinvader_customer_values(data)
        partner = self.write(self.partner.id, values)
        self._handle_shopinvader_customer_opt_in(partner, data)
        return partner

    def _get_shopinvader_customer_values(self, data: CustomerUpdate) -> dict:
        values = data.to_res_partner_vals()
        lang_id = data.lang_id
        if bool(lang_id):
            values["lang"] = self.env["res.lang"].browse(lang_id).code
        return values

    def _handle_shopinvader_customer_opt_in(self, partner, data: CustomerUpdate):
        self.ensure_one()
        opt_in = data.opt_in
        if opt_in is None:
            return
        Blacklist = self.env["mail.blacklist"].sudo()
        email = partner.email
        if not opt_in:
            Blacklist._add(email)
        else:
            Blacklist._remove(email)
        # as we return current partner data when updating,
        # we have to recompute is_blacklisted value ourselves
        partner._compute_is_blacklisted()


def customer_helper(
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
):
    return env["shopinvader_api_customer.router.helper"].new({"partner": partner})


@customer_router.get("/customer")
def get_customer_data(
    helper: Annotated[CustomerHelper, Depends(customer_helper)],
) -> Customer:
    """
    Get customer personal data of authenticated user
    """
    return Customer.from_res_partner(helper._get_customer())


@customer_router.post(
    "/customer",
)
def update_customer_data(
    data: CustomerUpdate,
    helper: Annotated[CustomerHelper, Depends(customer_helper)],
) -> Customer:
    """
    update customer personal data of authenticated user
    """
    updated_partner = helper._update_shopinvader_customer(data)
    return Customer.from_res_partner(updated_partner)
