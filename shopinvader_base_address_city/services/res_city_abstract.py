# Copyright 2023 KMEE INFORMATICA LTDA (http://www.kmee.com.br).
# @author Cristiano Rodrigues <cristiano.rodrigues@kmee.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, http
from odoo.exceptions import ValidationError

from odoo.addons.base_rest import restapi
from odoo.addons.component.core import AbstractComponent


class SearchServiceCities(AbstractComponent):
    _name = "search.service.cities"
    _inherit = "base.rest.service"
    _usage = "city"
    _description = "REST Services for Search cities across the state"

    @restapi.method(
        [(["/"], "GET")],
        input_param=restapi.CerberusValidator("_validator_search"),
        output_param=restapi.CerberusValidator("_validator_return_search"),
        cors="*",
    )
    def search(self, **params):
        country_code = params.get("country_code")
        state_code = params.get("state_code")
        try:
            country_id = self.env["res.country"].search([("code", "=", country_code)])

            if not country_id:
                country_id = self.shopinvader_backend.company_id.country_id

            if not country_id:
                return http.Response(
                    _(
                        {
                            "result": False,
                            "error": f"country_code: {country_code} not found",
                        }
                    ),
                    status=404,
                )

            if country_id:
                state_id = self.env["res.country.state"].search(
                    [("country_id", "=", country_id.id), ("code", "=", state_code)]
                )
                city_ids = self.env["res.city"].search(
                    [("country_id", "=", country_id.id), ("state_id", "=", state_id.id)]
                )

                res = []
                if not city_ids:
                    res.append({"id": state_id.id, "name": state_id.name})

                for x in city_ids:
                    res.append({"id": x.id, "name": x.name})

                if not state_id:
                    return http.Response(
                        _(
                            {
                                "result": False,
                                "error": f"state_code: {state_code} not found",
                            }
                        ),
                        status=404,
                    )
                elif not city_ids:
                    return http.Response(
                        _({"result": False, "error": "Cities: not found"}), status=404
                    )

        except ValidationError as e:
            return http.Response(_({"result": False, "error": str(e)}), status=404)

        return {"result": res}

    def _validator_search(self):
        return {
            "country_code": {"type": "string", "required": True},
            "state_code": {"type": "string", "required": True},
        }

    def _validator_return_search(self):
        return {
            "result": {
                "type": "list",
                "required": True,
                "schema": {
                    "type": "dict",
                    "schema": {
                        "name": {
                            "type": "string",
                            "required": True,
                            "nullable": True,
                        },
                        "id": {"type": "integer", "required": True},
                    },
                },
            },
        }
