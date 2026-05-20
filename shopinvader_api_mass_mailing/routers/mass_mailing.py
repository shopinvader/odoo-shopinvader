# Copyright 2026 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from typing import Annotated

from fastapi import APIRouter, Depends

from odoo import api, fields
from odoo.exceptions import MissingError
from odoo.tools import email_normalize

from odoo.addons.fastapi.dependencies import fastapi_endpoint, odoo_env
from odoo.addons.fastapi.models import FastapiEndpoint
from odoo.addons.shopinvader_router_helper import VirtualModel

from ..schemas import SubscribeInput, Subscription, UnsubscribeInput

mass_mailing_router = APIRouter(tags=["mass_mailing"])


class MassMailingHelper(VirtualModel):
    _inherit = "shopinvader.router.helper"
    _name = "shopinvader_api_mass_mailing.routers.helper"
    _description = "Shopinvader Mass Mailing Router Helper"

    endpoint_id = fields.Many2one(comodel_name="fastapi.endpoint")

    def _get_mailing_list(self):
        return self.endpoint_id.mailing_list_id

    def _prepare_contact_values(self, data: SubscribeInput, mailing_list) -> dict:
        return {
            "name": data.name,
            "email": data.email,
            "list_ids": [(4, mailing_list.id)],
        }

    def subscribe(self, data: SubscribeInput):
        mailing_list = self._get_mailing_list()
        if not mailing_list:
            raise MissingError(
                self.env._("No mass mailing list configured for this endpoint")
            )
        email_normalized = email_normalize(data.email)
        contact = (
            self.env["mailing.contact"]
            .with_context(active_test=False)
            .search([("email_normalized", "=", email_normalized)])
        )
        if contact:
            mailing_list.sudo()._update_subscription_from_email(
                data.email, opt_out=False
            )
            contact.write({"name": data.name, "list_ids": [(4, mailing_list.id)]})

        else:
            contact = self.env["mailing.contact"].create(
                self._prepare_contact_values(data, mailing_list)
            )
        return contact

    def unsubscribe(self, data: UnsubscribeInput):
        mailing_list = self._get_mailing_list()
        if not mailing_list:
            raise MissingError(
                self.env._("No mass mailing list configured for this endpoint")
            )

        mailing_list.sudo()._update_subscription_from_email(data.email, opt_out=True)
        # Don't leak the existence of the contact,
        # so we don't search for it and just return


def mass_mailing_helper(
    env: Annotated[api.Environment, Depends(odoo_env)],
    endpoint: Annotated[FastapiEndpoint, Depends(fastapi_endpoint)],
):
    return env["shopinvader_api_mass_mailing.routers.helper"].new(
        {
            "endpoint_id": endpoint.id,
        }
    )


@mass_mailing_router.post("/mass_mailing/subscribe")
def subscribe(
    data: SubscribeInput,
    helper: Annotated[MassMailingHelper, Depends(mass_mailing_helper)],
) -> Subscription | None:
    return Subscription.from_mailing_contact(helper.subscribe(data))


@mass_mailing_router.post("/mass_mailing/unsubscribe", status_code=204)
def unsubscribe(
    data: UnsubscribeInput,
    helper: Annotated[MassMailingHelper, Depends(mass_mailing_helper)],
) -> None:
    helper.unsubscribe(data)
