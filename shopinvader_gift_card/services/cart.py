# Copyright (C) 2022 Akretion (<http://www.akretion.com>).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date

from odoo.addons.base_rest.components.service import to_bool
from odoo.addons.component.core import Component


def to_date(value):
    return date.fromisoformat(value)


class CartService(Component):
    _inherit = "shopinvader.cart.service"

    def _convert_one_line(self, line):
        if line.gift_card_id:
            line.price_unit = line.gift_card_id.initial_amount
        res = super()._convert_one_line(line)
        res.update(self._get_gift_card_id(line))
        return res

    def _get_gift_card_id(self, line):
        return {"gift_card_id": line.gift_card_id.id}

    def add_item(self, **params):
        gift_card_tmpl_id = params.get("gift_card_tmpl_id")
        gift_card_tmpl = self.env["gift.card.template"].search(
            [("id", "=", gift_card_tmpl_id)], limit=1
        )
        if gift_card_tmpl:
            card = self._add_gift_card(gift_card_tmpl, params)
            params["gift_card_id"] = card.id
        return super().add_item(**params)

    def _prepare_cart_item(self, params, cart):
        res = super()._prepare_cart_item(params, cart)
        res.update(self._gift_card_values_from_params(params))
        return res

    def _gift_card_values_from_params(self, params):
        if "gift_card_id" in params:
            return {
                "gift_card_id": params.pop("gift_card_id") or False,
            }
        return {}

    def _add_item(self, cart, params):
        self._check_allowed_product(cart, params)
        item = self._check_existing_cart_item(cart, params)
        if hasattr(item, "gift_card_id"):
            with self.env.norecompute():
                self._create_cart_line(cart, params)
            cart.recompute()
            return item
        else:
            return super()._add_item(cart, params)

    def _add_gift_card(self, gift_card_tmpl, params):
        card = self.env["gift.card"].create(
            {
                "initial_amount": params.get("initial_amount"),
                "is_divisible": gift_card_tmpl.is_divisible,
                "duration": gift_card_tmpl.duration,
                "gift_card_tmpl_id": gift_card_tmpl.id,
                "start_date": params.get("start_date"),
                "comment": params.get("comment"),
                "beneficiary_name": params.get("beneficiary_name"),
                "beneficiary_email": params.get("beneficiary_email"),
                "buyer_id": params.get("buyer_id"),
                "buyer_name": params.get("buyer_name"),
                "buyer_email": params.get("buyer_email"),
                "state": "draft",
                "shopinvader_backend_id": self.shopinvader_backend.id,
            }
        )
        return card

    def _get_gift_card_schema(self):
        return {
            "initial_amount": {"coerce": float, "required": False, "type": "float"},
            "is_divisible": {"coerce": to_bool, "type": "boolean"},
            "duration": {"coerce": int, "required": False, "type": "integer"},
            "gift_card_tmpl_id": {"coerce": int, "required": False, "type": "integer"},
            "start_date": {"type": "date", "coerce": to_date},
            "comment": {"type": "string", "required": False},
            "beneficiary_name": {"type": "string", "required": False},
            "beneficiary_email": {"type": "string", "required": False},
            "buyer_id": {
                "coerce": int,
                "required": False,
                "type": "integer",
            },
            "buyer_name": {"type": "string", "required": False},
            "buyer_email": {"type": "string", "required": False},
            "state": {"type": "string", "required": False},
            "gift_card_id": {"coerce": int, "required": False, "type": "integer"},
        }

    def _validator_add_item(self):
        res = super()._validator_add_item()
        res.update(self._get_gift_card_schema())
        return res

    def _validator_update_item(self):
        res = super()._validator_update_item()
        res.update(self._get_gift_card_schema())
        return res
