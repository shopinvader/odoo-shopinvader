import ast

from odoo import _
from odoo.exceptions import MissingError, UserError

from odoo.addons.base_rest import restapi
from odoo.addons.component.core import Component


class CustomerService(Component):
    _inherit = "shopinvader.customer.service"

    def _jsonify_available_customers(self):
        return [
            "id",
            "name",
            "email",
            "street",
            "street2",
            "zip",
            "city",
            ("state_id", ["id", "name"]),
            ("country_id", ["id", "name"]),
            ("parent_id", ["id", "name"]),
        ]

    def _validator_return_available_customers(self):
        return {
            "id": {
                "type": "integer",
                "required": True,
                "nullable": False,
            },
            "name": {
                "type": "string",
                "required": True,
                "nullable": False,
            },
            "email": {
                "type": "string",
                "required": True,
                "nullable": True,
            },
            "street": {
                "type": "string",
                "required": True,
                "nullable": True,
            },
            "street2": {
                "type": "string",
                "required": True,
                "nullable": True,
            },
            "zip": {
                "type": "string",
                "required": True,
                "nullable": True,
            },
            "city": {
                "type": "string",
                "required": True,
                "nullable": True,
            },
            "state_id": {
                "type": "dict",
                "schema": {
                    "id": {
                        "type": "integer",
                        "required": True,
                        "nullable": False,
                    },
                    "name": {
                        "type": "string",
                        "required": True,
                        "nullable": False,
                    },
                },
                "nullable": True,
            },
            "country_id": {
                "type": "dict",
                "schema": {
                    "id": {
                        "type": "integer",
                        "required": True,
                        "nullable": False,
                    },
                    "name": {
                        "type": "string",
                        "required": True,
                        "nullable": False,
                    },
                },
                "nullable": True,
            },
            "parent_id": {
                "type": "dict",
                "schema": {
                    "id": {
                        "type": "integer",
                        "required": True,
                        "nullable": False,
                    },
                    "name": {
                        "type": "string",
                        "required": True,
                        "nullable": False,
                    },
                },
                "nullable": True,
            },
        }

    def _available_customers(self):
        return self.env["res.partner"].search(
            ast.literal_eval(self.shopinvader_backend.seller_access_customer_domain)
        )

    @restapi.method(
        [(["/available_customers"], "GET")],
        output_param=restapi.CerberusListValidator(
            "_validator_return_available_customers", unique_items=True
        ),
    )
    def available_customers(self):
        self.check_seller_access()
        return self._available_customers().jsonify(self._jsonify_available_customers())

    def update(self, _id, **params):
        try:
            return super().update(_id, **params)
        except MissingError as e:
            if not self.has_seller_access:
                raise e

            partner = self._available_customers().filtered(lambda x: x.id == _id)
            if partner:
                if params.keys() != {"email"}:
                    raise UserError(
                        _("You can only update the customer email as seller")
                    )

                partner.write(params)

                self._post_update(self.work.partner)

                return self.get()

            raise e
