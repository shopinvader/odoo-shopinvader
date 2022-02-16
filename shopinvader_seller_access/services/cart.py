from odoo import _
from odoo.exceptions import MissingError

from odoo.addons.base_rest import restapi
from odoo.addons.base_rest.components.service import to_int
from odoo.addons.component.core import Component


class CartService(Component):
    _inherit = "shopinvader.cart.service"

    @restapi.method(
        [(["/create_for"], "POST")],
        input_param=restapi.CerberusValidator("_validator_create_for"),
    )
    def create_for(self, customer_id, **params):
        self.check_seller_access()

        partner = self.env["res.partner"].browse(customer_id)
        if not partner.exists():
            raise MissingError(_("Customer {} not found".format(customer_id)))
        seller = self.partner.user_ids
        if not seller:
            raise MissingError(_("Partner {} is not a user".format(self.partner.email)))
        old_partner = self.work.partner
        self.work.partner = partner
        rv = self._to_json(self._create_empty_cart(user_id=seller.id))
        self.work.partner = old_partner
        return rv

    def _validator_create_for(self):
        return {
            "customer_id": {
                "coerce": to_int,
                "required": True,
                "type": "integer",
            }
        }

    def _get_cart_domain(self, filter_partner=False):
        domain = super()._get_cart_domain(filter_partner)
        # Here we add the possibility to fetch a cart if we are the seller
        if (
            self.has_seller_access
            and (self.shopinvader_backend.restrict_cart_to_partner or filter_partner)
            and self.partner.user_ids
        ):
            try:
                partner_filter_index = domain.index(
                    ("partner_id", "=", self.partner.id)
                )
            except ValueError:
                return domain

            domain.insert(
                partner_filter_index + 1, ("user_id", "=", self.partner.user_ids.id)
            )
            domain.insert(partner_filter_index, "|")
        return domain

    def _validator_return_available_carts(self):
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
            "state": {
                "type": "string",
                "required": True,
                "nullable": False,
            },
            "partner": {
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
            "typology": {
                "type": "string",
                "required": True,
                "nullable": False,
            },
            "date": {
                "type": "datetime",
                "required": True,
                "nullable": False,
            },
            "count": {
                "type": "float",
                "required": True,
                "nullable": False,
            },
            "amount_total": {
                "type": "float",
                "required": True,
                "nullable": False,
            },
        }

    def _convert_one_available_cart(self, sale):
        return {
            "id": sale.id,
            "name": sale.name,
            "state": sale.shopinvader_state,
            "partner": {"id": sale.partner_id.id, "name": sale.partner_id.name},
            "typology": sale.typology,
            "date": sale.date_order,
            "count": self._convert_lines(sale)["count"],
            "amount_total": self._convert_amount(sale)["total"],
        }

    @restapi.method(
        [(["/available_carts"], "GET")],
        output_param=restapi.CerberusListValidator("_validator_return_available_carts"),
    )
    def available_carts(self):
        self.check_seller_access()
        return [
            self._convert_one_available_cart(sale)
            for sale in self.env["sale.order"].search(self._get_cart_domain(True))
        ]