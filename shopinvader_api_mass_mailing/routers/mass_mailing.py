# Copyright 2026 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from typing import Annotated

from fastapi import APIRouter, Depends

from odoo import _, api, fields, models
from odoo.exceptions import MissingError
from odoo.tools import email_normalize

from odoo.addons.fastapi.dependencies import fastapi_endpoint, odoo_env
from odoo.addons.fastapi.models import FastapiEndpoint

from ..schemas import SubscribeInput, Subscription, UnsubscribeInput

mass_mailing_router = APIRouter(tags=["mass_mailing"])


class ShopinvaderMassMailingRouterHelper(models.AbstractModel):
    _name = "shopinvader_api_mass_mailing.routers.helper"
    _description = "Shopinvader Mass Mailing Router Helper"

    endpoint_id = fields.Many2one(comodel_name="fastapi.endpoint")

    def _get_mailing_list(self):
        return self.endpoint_id.mailing_list_id

    def _prepare_contact_values(self, data: SubscribeInput, mailing_list) -> dict:
        name, email = self.env["mailing.contact"].get_name_email(
            f"{data.name} <{data.email}>" if data.name else data.email
        )
        return {
            "name": name,
            "email": email,
            "list_ids": [(4, mailing_list.id)],
        }

    def subscribe(self, data: SubscribeInput):
        mailing_list = self._get_mailing_list()
        if not mailing_list:
            raise MissingError(_("No mass mailing list configured for this endpoint"))

        contact = (
            self.env["mailing.contact"]
            .with_context(active_test=False)
            .search([("email_normalized", "=", email_normalize(data.email))])
        )
        if contact:
            self.env["mailing.mailing"].update_opt_out(
                data.email, mailing_list.ids, False
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
            raise MissingError(_("No mass mailing list configured for this endpoint"))

        self.env["mailing.mailing"].update_opt_out(data.email, mailing_list.ids, True)
        # Don't leak the existence of the contact, so we don't search for it and just return


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
    helper: Annotated[ShopinvaderMassMailingRouterHelper, Depends(mass_mailing_helper)],
) -> Subscription | None:
    return Subscription.from_mailing_contact(helper.subscribe(data))


@mass_mailing_router.post("/mass_mailing/unsubscribe", status_code=204)
def unsubscribe(
    data: UnsubscribeInput,
    helper: Annotated[ShopinvaderMassMailingRouterHelper, Depends(mass_mailing_helper)],
) -> None:
    helper.unsubscribe(data)
