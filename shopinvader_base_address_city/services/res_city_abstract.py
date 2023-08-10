# Copyright 2023 KMEE INFORMATICA LTDA (http://www.kmee.com.br).
# @author Cristiano Rodrigues <cristiano.rodrigues@kmee.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError, ValidationError

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
        state = params.get("state")
        try:
            country_id = self.shopinvader_backend.company_id.country_id
            if country_id:
                state_id = self.env["res.country.state"].search(
                    [("country_id", "=", country_id.id), ("code", "=", state)]
                )
                city_ids = self.env["res.city"].search(
                    [("country_id", "=", country_id.id), ("state_id", "=", state_id.id)]
                )
                cities = []
                for x in city_ids:
                    cities.append({"name": x.name, "id": x.id})
        except (UserError, ValidationError) as e:
            return {"result": False, "error": str(e)}

        return {"result": cities}

    def _validator_search(self):
        return {
            "state": {"type": "string", "required": True},
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
