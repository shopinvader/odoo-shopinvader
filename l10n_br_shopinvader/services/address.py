# Copyright 2022 KMEE (http://www.kmee.com.br).
# @author Cristiano Rodrigues <cristiano.rodrigues@kmee.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json

from odoo.http import Response

from odoo.addons.base_rest import restapi
from odoo.addons.base_rest.components.service import to_int
from odoo.addons.component.core import Component


class AddressService(Component):
    _inherit = "shopinvader.partner.service.mixin"

    def _json_parser(self):
        res = super()._json_parser()
        res.append("legal_name")
        res.append("cnpj_cpf")
        res.append("inscr_est")

        return res

    def _validator_create(self):
        res = super()._validator_create()

        res["zip"]["required"] = False
        res["country"]["required"] = False

        res["inscr_est"] = {
            "type": "string",
            "required": False,
        }
        res["cnpj_cpf"] = {
            "type": "string",
            "required": False,
        }
        res["email"] = {
            "type": "string",
            "required": False,
        }
        res["legal_name"] = {
            "type": "string",
            "required": False,
        }
        res["state"] = {
            "type": "dict",
            "schema": {
                "id": {
                    "coerce": to_int,
                    "nullable": False,
                    "type": "integer",
                },
                "code": {
                    "type": "string",
                    "nullable": False,
                },
            },
        }

        return res

    def _validator_update(self):
        res = super()._validator_update()
        return res

    def _prepare_params(self, params, mode="create"):
        if params.get("city_id"):
            params["city_id"] = (
                params.get("city_id")["id"]
                if type(params["city_id"]) == dict
                else params.get("city_id")
            )

        if params["state"]["id"] and not params["state"]["code"]:
            params["state_id"] = (
                params["state"]["id"]
                if type(params["state_id"]) == dict
                else params["state"]
            )
        if params["state"]["code"]:
            if params["country"]:
                state_id = self.env["res.country.state"].search(
                    [
                        ("code", "=", params["state"]["code"]),
                        ("country_id", "=", params["country"]["id"]),
                    ]
                )

        res = super(AddressService, self)._prepare_params(params, mode)
        res["state_id"] = state_id.id
        return res

    @restapi.method(
        [(["/zip-code"], "POST")],
        input_param=restapi.CerberusValidator("_validator_zip_code"),
        output_param=restapi.CerberusValidator("_validator_return_zip_code"),
        cors="*",
    )
    def zip_code(self, **params):
        zip_code = params.get("zip_code")
        try:
            address = self.env["l10n_br.zip"]._consultar_cep(zip_code)
        except Exception as e:
            return Response(
                json.dumps(str(e)), content_type="application/json", status=404
            )
        res = self.env["res.city"].search([("id", "=", address["city_id"])])
        city = {"id": res.id, "name": res.name}
        state = {
            "id": res.state_id.id,
            "name": res.state_id.display_name,
            "code": res.state_id.code,
        }
        country = {"id": res.country_id.id, "name": res.country_id.display_name}

        return {
            "zip_code": address["zip_code"],
            "street_name": address["street_name"],
            "zip_complement": address["zip_complement"],
            "district": address["district"],
            "city_id": city,
            "state_id": state,
            "country_id": country,
        }

    def _validator_zip_code(self):
        return {
            "zip_code": {"type": "string", "required": True},
        }

    def _validator_return_zip_code(self):
        """
        Street and district are not required because some
        cities have only one CEP, so these fields might come
        empty from the API call
        """

        return {
            "zip_code": {
                "type": "string",
                "required": True,
            },
            "street_name": {
                "type": "string",
                "required": False,
                "nullable": True,
            },
            "zip_complement": {
                "type": "string",
                "required": False,
                "nullable": True,
            },
            "district": {
                "type": "string",
                "required": False,
                "nullable": True,
            },
            "city_id": {
                "type": "dict",
                "schema": {
                    "id": {
                        "type": "integer",
                        "required": False,
                    },
                    "name": {
                        "type": "string",
                        "required": False,
                    },
                },
            },
            "state_id": {
                "type": "dict",
                "schema": {
                    "id": {
                        "type": "integer",
                        "required": True,
                    },
                    "name": {
                        "type": "string",
                        "required": True,
                    },
                    "code": {
                        "type": "string",
                        "required": True,
                    },
                },
            },
            "country_id": {
                "type": "dict",
                "schema": {
                    "id": {
                        "type": "integer",
                        "required": True,
                    },
                    "name": {
                        "type": "string",
                        "required": True,
                    },
                },
            },
        }

    @restapi.method(
        [(["/states"], "GET")],
        input_param=restapi.CerberusValidator("_validator_states"),
        output_param=restapi.CerberusValidator("_validator_return_states"),
        cors="*",
    )
    def search_states(self, **params):
        """Return a list of states registered on the database."""

        country_code = params.get("country_code")
        shopinvader_backend = self.env["shopinvader.backend"].browse()
        allowed_country = shopinvader_backend.allowed_country_ids.search(
            [("code", "=", country_code)]
        )
        state_ids = self.env["res.country.state"].search(
            [("country_id.code", "=", country_code)]
        )
        if allowed_country and state_ids:
            if state_ids:
                states = []
                for state in state_ids:
                    states += [{"id": state.id, "name": state.name, "code": state.code}]
            return {"state_ids": states}
        return {
            "state_ids": [
                {"id": False, "name": "", "code": ""},
            ]
        }

    def _validator_states(self):
        return {
            "country_code": {"type": "string", "required": True},
        }

    @staticmethod
    def _validator_return_states():
        return {
            "state_ids": {
                "type": "list",
                "schema": {
                    "type": "dict",
                    "schema": {
                        "id": {
                            "type": "integer",
                            "required": True,
                            "nullable": True,
                        },
                        "name": {
                            "type": "string",
                            "required": True,
                            "nullable": True,
                        },
                        "code": {
                            "type": "string",
                            "required": True,
                            "nullable": True,
                        },
                    },
                },
            },
        }
