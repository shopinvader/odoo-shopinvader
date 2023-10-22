from odoo.addons.component.core import Component


class CartService(Component):
    _inherit = "shopinvader.cart.service"

    def _adapt_batch_params_with_skip_coupon_recompute(self, params):
        # Skip coupon recompute for all items except the last one
        batch = params.pop("batch", None)
        if not batch:
            return params

        batch_with_skip_coupon_recompute = [
            {**params, "skip_coupon_recompute": True} for params in batch
        ]
        skip_coupon_recompute = params.pop("skip_coupon_recompute", None)
        batch_with_skip_coupon_recompute[-1][
            "skip_coupon_recompute"
        ] = skip_coupon_recompute

        return {
            **params,
            "batch": batch_with_skip_coupon_recompute,
        }

    def add_items(self, **params):
        return super().add_items(
            **self._adapt_batch_params_with_skip_coupon_recompute(params)
        )

    def update_items(self, **params):
        return super().update_items(
            **self._adapt_batch_params_with_skip_coupon_recompute(params)
        )

    def delete_items(self, **params):
        return super().delete_items(
            **self._adapt_batch_params_with_skip_coupon_recompute(params)
        )

    def _remove_subvalidator_skip_coupon_recompute(self, validator):
        if "skip_coupon_recompute" in validator:
            del validator["skip_coupon_recompute"]
        return validator

    def _validator_add_items(self):
        return {
            "batch": {
                "type": "list",
                "schema": {
                    "type": "dict",
                    "schema": self._remove_subvalidator_skip_coupon_recompute(
                        self._validator_add_item()
                    ),
                },
            },
            **self._subvalidator_skip_coupon_recompute(),
        }

    def _validator_update_items(self):
        return {
            "batch": {
                "type": "list",
                "schema": {
                    "type": "dict",
                    "schema": self._remove_subvalidator_skip_coupon_recompute(
                        self._validator_update_item()
                    ),
                },
            },
            **self._subvalidator_skip_coupon_recompute(),
        }

    def _validator_delete_items(self):
        return {
            "batch": {
                "type": "list",
                "schema": {
                    "type": "dict",
                    "schema": self._remove_subvalidator_skip_coupon_recompute(
                        self._validator_delete_item()
                    ),
                },
            },
            **self._subvalidator_skip_coupon_recompute(),
        }
