from odoo.addons.component.core import Component


class CartService(Component):
    _inherit = "shopinvader.cart.service"

    def add_items(self, **params):
        batch = params.pop("batch", None)
        if not batch:
            return self._to_json(self._get())

        cart = self._get(create_if_not_found=False)
        if not cart:
            cart_params = self._add_item_create_cart_params(**batch[0])
            cart = self._create_empty_cart(**cart_params)

        for params in batch:
            try:
                self._add_item(cart, params)
            except Exception as e:
                new_exception = type(e)(
                    "Error while adding item %s to cart: %s"
                    % (
                        params["product_id"],
                        e,
                    )
                )
                # Add useful info to json exception response
                new_exception.rest_json_info = {
                    "product_id": params["product_id"],
                }
                raise new_exception from e
        return self._to_json(cart)

    def update_items(self, **params):
        batch = params.pop("batch", None)
        if not batch:
            return self._to_json(self._get())
        cart = self._get()
        for params in batch:
            try:
                self._update_item(cart, params)
            except Exception as e:
                new_exception = type(e)(
                    "Error while updating item %s to cart: %s"
                    % (
                        params["item_id"],
                        e,
                    )
                )
                # Add useful info to json exception response
                new_exception.rest_json_info = {
                    "item_id": params["item_id"],
                }
                raise new_exception from e
        return self._to_json(cart)

    def delete_items(self, **params):
        batch = params.pop("batch", None)
        if not batch:
            return self._to_json(self._get())
        cart = self._get()
        for params in batch:
            try:
                self._delete_item(cart, params)
            except Exception as e:
                new_exception = type(e)(
                    "Error while deleting item %s to cart: %s"
                    % (
                        params["item_id"],
                        e,
                    )
                )
                # Add useful info to json exception response
                new_exception.rest_json_info = {
                    "item_id": params["item_id"],
                }
                raise new_exception from e
        return self._to_json(cart)

    def _validator_add_items(self):
        return {
            "batch": {
                "type": "list",
                "schema": {
                    "type": "dict",
                    "schema": self._validator_add_item(),
                },
            }
        }

    def _validator_update_items(self):
        return {
            "batch": {
                "type": "list",
                "schema": {
                    "type": "dict",
                    "schema": self._validator_update_item(),
                },
            }
        }

    def _validator_delete_items(self):
        return {
            "batch": {
                "type": "list",
                "schema": {
                    "type": "dict",
                    "schema": self._validator_delete_item(),
                },
            }
        }
