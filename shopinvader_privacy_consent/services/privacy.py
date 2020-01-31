# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _
from odoo.addons.base_rest.components.service import to_bool
from odoo.addons.component.core import Component
from odoo.fields import first
from odoo.osv import expression


class CustomerService(Component):

    _name = "shopinvader.privacy.service"
    _inherit = "base.shopinvader.service"
    _usage = "privacy"

    def consent(self, **params):
        """
        Search for a draft or sent consent for the connected partner.
        If not found, create a new one.
        :param params: consent type boolean
        :return:
        """
        consent_ids = self.env["privacy.consent"].search(
            self._get_privacy_consent_domain()
        )
        if consent_ids:
            consent = first(consent_ids)
            consent.action_answer(answer=params.get("consent"))
        else:
            self.env["privacy.consent"].create(
                self._prepare_consent_data(params.get("consent"))
            )
        return {"result": True}

    def search(self, **params):
        """

        :param params: consent type boolean
        :return:
        """
        consent_ids = self.env["privacy.consent"].search(
            self._get_privacy_consent_domain()
        )
        res = dict()
        res["data"] = consent_ids.jsonify(self._json_parser())
        return res

    def _prepare_consent_data(self, accepted):
        """
        Prepare consent data for a new one
        :param accepted: boolean
        :return:
        """
        return {
            "activity_id": self.shopinvader_backend.privacy_activity_id.id,
            "partner_id": self.partner.id,
            "accepted": accepted,
            "state": "answered",
        }

    def _check_with_activity(self, field, value, error):
        """
        Implements 'check_with' validation for activity linked to backend
        :param field:
        :param value:
        :param error:
        :return:
        """
        if not self.shopinvader_backend.privacy_activity_id:
            error(field, _("The backend is not linked to an activity!"))

    def _json_parser(self):
        """
        List of consent properties exposed
        :return:
        """
        res = ["id", "accepted", "accepted_date", "refusal_date"]
        return res

    def _to_json(self, consent):
        accepted_date = consent.accepted_date
        refusal_date = consent.refusal_date
        return {
            "accepted": consent.accepted,
            "accepted_date": accepted_date if accepted_date else "",
            "refusal_date": refusal_date if refusal_date else "",
        }

    def _validator_consent(self):
        schema = {
            "consent": {
                "coerce": to_bool,
                "type": "boolean",
                "required": True,
                "check_with": self._check_with_activity,
            }
        }
        return schema

    def _validator_return_consent(self):
        """
        Returns the result of privacy consent
        :return:
        """
        schema = {"result": {"type": "boolean", "required": True}}
        return schema

    def _validator_search(self):
        """
        Search does not require parameters
        :return:
        """
        schema = {}
        return schema

    def _validator_return_search(self):
        """
        Should returns a list of consents
        :return:
        """
        consent_schema = {
            "id": {"type": "integer"},
            "accepted": {"type": "boolean"},
            "accepted_date": {
                "type": "string",
                "required": False,
                "nullable": True,
            },
            "refusal_date": {
                "type": "string",
                "required": False,
                "nullable": True,
            },
        }
        schema = {
            "data": {
                "type": "list",
                "schema": {"type": "dict", "schema": consent_schema},
            }
        }
        return schema

    def _get_privacy_consent_domain(self):
        """
        Returns the consents linked to the connected partner linked to
        the backend.
        If the backend has no activity linked, returns nothing.
        :return:
        """
        if not self.shopinvader_backend.privacy_activity_id:
            return expression.FALSE_DOMAIN
        return [
            (
                "activity_id",
                "=",
                self.shopinvader_backend.privacy_activity_id.id,
            ),
            ("partner_id", "=", self.partner.id),
        ]
