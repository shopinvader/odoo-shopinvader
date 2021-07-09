# Copyright 2021 Camptocamp SA
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class CartService(Component):
    _inherit = "shopinvader.cart.service"

    # Public Methods

    def apply_coupon(self, **params):
        cart = self._get()
        self._apply_coupon(cart, params)
        return self._to_json(cart)

    def recompute_coupon_lines(self, **params):
        cart = self._get()
        self._recompute_coupon_lines(cart, params)
        return self._to_json(cart)

    # Private Methods

    def _apply_coupon(self, cart, params):
        """Apply a coupon or promotion code.

        It can raise UserError if coupon is not applicable.
        """
        return (
            self.env["sale.coupon.apply.code"]
            .with_context(active_id=cart.id)
            .create({"coupon_code": params["code"]})
            .process_coupon()
        )

    def _recompute_coupon_lines(self, cart, params):
        cart.recompute_coupon_lines()

    # Private Overrides

    def _add_item(self, cart, params):
        skip_coupon_recompute = params.pop("skip_coupon_recompute", None)
        res = super()._add_item(cart, params)
        if not skip_coupon_recompute:
            self._recompute_coupon_lines(cart, params)
        return res

    def _update_item(self, cart, params, item=False):
        skip_coupon_recompute = params.pop("skip_coupon_recompute", None)
        res = super()._update_item(cart, params, item)
        if not skip_coupon_recompute:
            self._recompute_coupon_lines(cart, params)
        return res

    def _delete_item(self, cart, params):
        skip_coupon_recompute = params.pop("skip_coupon_recompute", None)
        res = super()._delete_item(cart, params)
        if not skip_coupon_recompute:
            self._recompute_coupon_lines(cart, params)
        return res

    def _get_lines_to_copy(self, cart):
        return super()._get_lines_to_copy(cart).filtered(lambda l: not l.is_reward_line)

    # Validator

    def _validator_apply_coupon(self):
        return {
            "code": {
                "type": "string",
                "required": True,
            }
        }

    def _validator_recompute_coupon_lines(self):
        return {}

    def _subvalidator_skip_coupon_recompute(self):
        return {
            "skip_coupon_recompute": {
                "type": "boolean",
                "required": False,
            }
        }

    def _validator_add_item(self):
        res = super()._validator_add_item()
        res.update(self._subvalidator_skip_coupon_recompute())
        return res

    def _validator_update_item(self):
        res = super()._validator_update_item()
        res.update(self._subvalidator_skip_coupon_recompute())
        return res

    def _validator_delete_item(self):
        res = super()._validator_delete_item()
        res.update(self._subvalidator_skip_coupon_recompute())
        return res
