# Copyright 2021 Camptocamp (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class AddressService(Component):
    _inherit = "shopinvader.address.service"

    def _validator_create(self):
        schema = super()._validator_create()
        schema.update(
            {
                "newsletter_subscription": {
                    "type": "string",
                    "required": False,
                    "nullable": True,
                    "allowed": ["subscribed", "unsubscribed"],
                },
            }
        )
        return schema

    def _json_parser(self):
        parser = super()._json_parser()
        parser.extend(
            [
                "main_mailing_list_subscription_state:newsletter_subscription",
                "main_mailing_list_subscription_date:newsletter_subscription_date",
                "main_mailing_list_unsubscription_date:newsletter_unsubscription_date",
            ]
        )
        return parser

    def _prepare_params(self, params, mode="create"):
        params = super()._prepare_params(params, mode=mode)
        if "newsletter_subscription" in params:
            subs = params.pop("newsletter_subscription")
            params["main_mailing_list_subscription_state"] = subs
        return params
