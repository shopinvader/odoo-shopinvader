# -*- coding: utf-8 -*-
# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# pylint: disable=consider-merging-classes-inherited
import logging

from cerberus import Validator
from odoo.addons.base_rest.components.service import to_int
from odoo.addons.component.core import Component
from odoo.exceptions import UserError
from odoo.tools.translate import _
from werkzeug.exceptions import NotFound

from .. import shopinvader_response

_logger = logging.getLogger(__name__)


class CartService(Component):
    _inherit = "shopinvader.abstract.sale.service"
    _name = "shopinvader.cart.service"
    _usage = "cart"

    @property
    def cart_recompute_identify_key(self):
        return "sale.order._shopinvader_delayed_recompute.%s" % self.cart_id

    @property
    def cart_id(self):
        return self.shopinvader_session.get("cart_id", 0)

    # The following method are 'public' and can be called from the controller.

    def search(self):
        """Return the cart that have been set in the session or
           search an existing cart for the current partner"""
        if not self.cart_id:
            return {}
        # If the cart_id doesn't exist anymore, we don't have to create a new
        return self._to_json(self._get(create_if_not_found=False))

    def update(self, **params):
        cart = self._get()
        response = self._update(cart, params)
        if response.get("redirect_to"):
            return response
        else:
            return self._to_json(cart)

    def add_item(self, **params):
        """
        Add item to cart.
        Don't access to cart fields in this method. Do it in _add_item.
        The cart has to be recomputed
        :param params:
        :return:
        """
        simple_service = self.shopinvader_backend.simple_cart_service
        cart = self._get()
        if not cart:
            cart = self._create_empty_cart()
        # Modify the cart with no recomputation
        with self.env.norecompute():
            item = self._add_item(cart, params)
        self._launch_cart_recompute(cart, item)
        return self._to_json(cart, simple=simple_service)

    def update_item(self, **params):
        cart = self._get()
        self._update_item(cart, params)
        return self._to_json(cart)

    def delete_item(self, **params):
        cart = self._get()
        self._delete_item(cart, params)
        return self._to_json(cart)

    def clear(self):
        """
        Clear the current cart (by $session)
        :return: dict/json
        """
        cart = self._get()
        cart = self._clear_cart(cart)
        return self._to_json(cart)

    def _get_validator_cart_by_id_domain(self, value):
        """
        Get cart by id domain. Limiting to session partner.
        :param value:
        :return:
        """
        return [("partner_id", "=", self.partner.id), ("id", "=", value)]

    def _get_line_copy_vals(self, line):
        """
        Prepare copy values to be passed to _add_item
        :param line: sale.order.line
        :return: dict
        """
        return {
            "product_id": line.product_id.id,
            "item_qty": line.product_uom_qty,
        }

    def _get_lines_to_copy(self, cart):
        return cart.order_line

    # pylint: disable=W8102,W8106
    def copy(self, **params):
        """
        This service allows
        :param params:
        :return:
        """
        return self._copy(**params)

    def _copy(self, **params):
        """
        Copy the cart given by id without the lines
        They will be re-added
        :return: dict/json
        """
        cart = self.env["sale.order"].search(
            self._get_validator_cart_by_id_domain(params.get("id"))
        )
        # Copy the existing cart
        # Delete all lines and re-add them with 'shopinvader' flavour
        new_cart = cart.copy({"order_line": False, "typology": "cart"})
        for line in self._get_lines_to_copy(cart):
            vals = self._get_line_copy_vals(line)
            self._add_item(new_cart, vals)

        return self._to_json(new_cart)

    # Validator
    def _cart_validator_exists(self, field, value, error):
        """
        Implements 'check_with' validation
        :param field:
        :param value:
        :param error:
        :return:
        """
        cart = self.env["sale.order"].search(
            self._get_validator_cart_by_id_domain(value)
        )
        if len(cart) != 1:
            error(
                field, _("The cart does not exists or does not belong to you!")
            )

    def _validator_copy(self):
        return {
            "id": {
                "coerce": to_int,
                "required": True,
                "type": "integer",
                "check_with": self._cart_validator_exists,
            }
        }

    def _validator_return_copy(self):
        return Validator({}, allow_unknown=True)

    def _validator_search(self):
        return {}

    def _validator_clear(self):
        return {}

    def _subvalidator_shipping(self):
        return {
            "type": "dict",
            "schema": {
                "address": {
                    "type": "dict",
                    "schema": {"id": {"coerce": to_int}},
                }
            },
        }

    def _subvalidator_invoicing(self):
        return {
            "type": "dict",
            "schema": {
                "address": {
                    "type": "dict",
                    "schema": {"id": {"coerce": to_int}},
                }
            },
        }

    def _subvalidator_step(self):
        return {
            "type": "dict",
            "schema": {
                "current": {"type": "string"},
                "next": {"type": "string"},
            },
        }

    def _validator_update(self):
        return {
            "step": self._subvalidator_step(),
            "shipping": self._subvalidator_shipping(),
            "invoicing": self._subvalidator_invoicing(),
            "note": {"type": "string"},
        }

    def _validator_add_item(self):
        return {
            "product_id": {
                "coerce": to_int,
                "required": True,
                "type": "integer",
            },
            "item_qty": {"coerce": float, "required": True, "type": "float"},
        }

    def _validator_update_item(self):
        return {
            "item_id": {"coerce": to_int, "required": True, "type": "integer"},
            "item_qty": {"coerce": float, "required": True, "type": "float"},
        }

    def _validator_delete_item(self):
        return {
            "item_id": {"coerce": to_int, "required": True, "type": "integer"}
        }

    # The following method are 'private' and should be never never NEVER call
    # from the controller.
    # All params are trusted as they have been checked before

    def _launch_cart_recompute(self, cart, item):
        """
        Launches cart recompute depending the backend configuration
        :param cart:
        :param item:
        :return:
        """
        simple_service = self.shopinvader_backend.simple_cart_service
        if simple_service:
            # Recompute cart asynchronously to avoid latencies on frontend
            description = "Recompute cart %s" % (item.order_id.id)
            item.order_id.with_delay(
                description=description,
                priority=1,
                identity_key=self.cart_recompute_identify_key,
            )._shopinvader_delayed_recompute()
        else:
            cart.recompute()
            item.order_id.shopinvader_to_be_recomputed = False

    def _upgrade_cart_item_quantity(self, cart, item, product_qty):
        vals = {"product_uom_qty": product_qty}
        new_values = item.play_onchanges(vals, vals.keys())
        # clear cache after play onchange
        real_line_ids = [line.id for line in cart.order_line if line.id]
        cart._cache["order_line"] = tuple(real_line_ids)
        vals.update(new_values)
        item.write(vals)

    def _do_clear_cart_cancel(self, cart):
        """
        Cancel the existing cart.
        Don't need to create a new one because it'll done automatically
        when the customer will add a new item.
        :param cart: sale.order recordset
        :return: sale.order recordset
        """
        cart.action_cancel()
        return cart.browse()

    def _do_clear_cart_delete(self, cart):
        """
        Delete/unlink the given cart
        :param cart: sale.order recordset
        :return: sale.order recordset
        """
        cart.unlink()
        return cart.browse()

    def _do_clear_cart_clear(self, cart):
        """
        Remove items from given cart.
        :param cart: sale.order recordset
        :return: sale.order recordset
        """
        cart.write({"order_line": [(5, False, False)]})
        return cart

    def _clear_cart(self, cart):
        """
        Action to clear the cart, depending on the backend configuration.
        :param cart: sale.order recordset
        :return: sale.order recordset
        """
        clear_option = self.shopinvader_backend.clear_cart_options
        do_clear = "_do_clear_cart_%s" % clear_option
        if hasattr(self, do_clear):
            cart = getattr(self, do_clear)(cart)
        else:
            _logger.error("The %s function doesn't exists.", do_clear)
            raise NotImplementedError(_("Missing feature to clear the cart!"))
        return cart

    def _add_item(self, cart, params):
        existing_item = self._check_existing_cart_item(cart, params)
        if existing_item:
            qty = existing_item.product_uom_qty + params["item_qty"]
            self._upgrade_cart_item_quantity(cart, existing_item, qty)
        else:
            vals = self._prepare_cart_item(params, cart)
            new_values = self._sale_order_line_onchange(vals)
            vals.update(new_values)
            # As the frontend could be in several languages but we have only
            # one anonymous parnter with his language set, we need to ensure
            # that description on the line is in the right language
            partner = cart.partner_id
            ctx_lang = self.env.context.get("lang", partner.lang)
            if partner.lang != ctx_lang:
                product_id = vals["product_id"]
                vals["name"] = self._get_sale_order_line_name(product_id)
            existing_item = self.env["sale.order.line"].create(vals)
        existing_item.order_id.shopinvader_to_be_recomputed = True
        return existing_item

    def _get_sale_order_line_name(self, product_id):
        product = self.env["product.product"].browse(product_id)
        name = product.name_get()[0][1]
        if product.description_sale:
            name += "\n" + product.description_sale
        return name

    def _sale_order_line_onchange(self, vals):
        """
        Simulate the onchange on sale.order.line with given vals.
        :param vals: dict
        :return: dict
        """
        # the next statement is done with suspending the security for
        #  performance reasons. It is safe only if both 3 following
        # fields are filled on the sale order:
        # - company_id
        # - fiscal_position_id
        # - pricelist_id
        so_line_obj = self.env["sale.order.line"].suspend_security()
        new_values = so_line_obj.play_onchanges(vals, vals.keys())
        return new_values

    def _update_item(self, cart, params, item=False):
        if not item:
            item = self._get_cart_item(cart, params, raise_if_not_found=False)
        if item:
            self._upgrade_cart_item_quantity(cart, item, params["item_qty"])
            return
        # The item id is maybe the one from a previous cart.
        line_id = params["item_id"]
        line = self.env["sale.order.line"].search(
            [
                ("id", "=", line_id),
                ("order_id.partner_id", "=", cart.partner_id.id),
            ]
        )
        if line:
            # silently create a new line on the new cart from the previous
            # line. This case could occurs if the customer click on the add
            # button from within an old session still open in its browser
            add_item_params = self._prepare_add_item_params_from_line(line)
            add_item_params["item_qty"] = params["item_qty"]
            self._add_item(cart, add_item_params)
            return params["item_qty"]
        raise NotFound("No cart item found with id %s" % params["item_id"])

    def _delete_item(self, cart, params):
        item = self._get_cart_item(cart, params, raise_if_not_found=False)
        if item:
            item.unlink()

    def _prepare_add_item_params_from_line(self, sale_order_line):
        return {"product_id": sale_order_line.product_id.id, "item_qty": 1}

    def _prepare_shipping(self, shipping, params):
        if "address" in shipping:
            address = shipping["address"]
            # By default we always set the invoice address with the
            # shipping address, if you want a different invoice address
            # just pass it
            params["partner_shipping_id"] = address["id"]
            params["partner_invoice_id"] = params["partner_shipping_id"]

    def _prepare_invoicing(self, invoicing, params):
        if "address" in invoicing:
            params["partner_invoice_id"] = invoicing["address"]["id"]

    def _prepare_step(self, step, params):
        if "next" in step:
            params["current_step_id"] = self._get_step_from_code(
                step["next"]
            ).id
        if "current" in step:
            params["done_step_ids"] = [
                (4, self._get_step_from_code(step["current"]).id, 0)
            ]

    def _prepare_update(self, cart, params):
        if "shipping" in params:
            self._prepare_shipping(params.pop("shipping"), params)
        if "invoicing" in params:
            self._prepare_invoicing(params.pop("invoicing"), params)
        if "step" in params:
            self._prepare_step(params.pop("step"), params)
        return params

    def _update(self, cart, params):
        params = self._prepare_update(cart, params)
        if params:
            cart.write_with_onchange(params)
        return {}

    def _get_step_from_code(self, code):
        step = self.env["shopinvader.cart.step"].search([("code", "=", code)])
        if not step:
            raise UserError(_("Invalid step code %s") % code)
        else:
            return step

    def _to_json_simple(self, cart):
        """
        Returns simple and fast items
        :return: dict
        """
        cart_simple = cart.with_context(prefetch_fields=False)
        qty = sum(
            line.product_uom_qty
            for line in cart_simple.order_line
            if self._is_item(line)
        )
        return {"id": cart.id, "lines": {"count": qty}}

    def _to_json(self, cart, simple=False):
        """
        Return cart json depending on which type of service (simple or not)
        Modify Session response accordingly
        :param cart:
        :param simple:
        :return:
        """
        response = shopinvader_response.get()
        if not cart:
            response.set_session("cart_id", 0)
            response.set_store_cache("cart", {})
            return {"data": {}}
        if simple:
            res = self._to_json_simple(cart)
        else:
            res = super(CartService, self)._to_json(cart)[0]
        response.set_session("cart_id", res["id"])
        response.set_store_cache("cart", res)
        return {"data": res}

    def _get(self, create_if_not_found=True):
        """

        :return: sale.order recordset (cart)
        """
        cart = self.env["sale.order"].browse()
        if self.cart_id:
            # here we take advantage of the cache. If the cart has been
            # already loaded, no SQL query will be issued
            # an alternative would be to build a domain with the expected
            # criteria on the cart but in this case, each time the _get method
            # would have been called, a new SQL query would have been done
            cart = self.env["sale.order"].browse(self.cart_id).exists()
            # Recompute cart if needed (in case of simple service call)
            if cart:
                cart.shopinvader_recompute()
        if (
            cart.shopinvader_backend_id == self.shopinvader_backend
            and cart.typology == "cart"
            and cart.state == "draft"  # ensure that we only work on draft
        ):
            return cart
        if create_if_not_found:
            return self._create_empty_cart()
        return cart

    def _create_empty_cart(self):
        vals = self._prepare_cart()
        return self.env["sale.order"].create(vals)

    def _prepare_cart(self):
        partner = self.partner or self.shopinvader_backend.anonymous_partner_id
        vals = {
            "typology": "cart",
            "partner_id": partner.id,
            "partner_shipping_id": partner.id,
            "partner_invoice_id": partner.id,
            "shopinvader_backend_id": self.shopinvader_backend.id,
        }
        vals.update(self.env["sale.order"].play_onchanges(vals, vals.keys()))
        if self.shopinvader_backend.account_analytic_id.id:
            vals[
                "project_id"
            ] = self.shopinvader_backend.account_analytic_id.id
        if self.shopinvader_backend.pricelist_id:
            # We must always force the pricelist. In the case of sale_profile
            # the pricelist is not set on the backend
            vals.update(
                {"pricelist_id": self.shopinvader_backend.pricelist_id.id}
            )
        if self.shopinvader_backend.sequence_id:
            vals["name"] = self.shopinvader_backend.sequence_id._next()
        return vals

    def _get_onchange_trigger_fields(self):
        return ["partner_id", "partner_shipping_id", "partner_invoice_id"]

    def _check_call_onchange(self, params):
        onchange_fields = self._get_onchange_trigger_fields()
        for changed_field in params.keys():
            if changed_field in onchange_fields:
                return True
        return False

    def _get_cart_item(self, cart, params, raise_if_not_found=True):
        # We search the line based on the item id and the cart id
        # indeed the item_id information is given by the
        # end user (untrusted data) and the cart id by the
        # locomotive server (trusted data)
        item = cart.mapped("order_line").filtered(
            lambda l, id_=params["item_id"]: l.id == id_
        )
        if not item and raise_if_not_found:
            raise NotFound("No cart item found with id %s" % params["item_id"])
        return item

    def _check_existing_cart_item(self, cart, params):
        product_id = params["product_id"]
        order_lines = cart.order_line
        return order_lines.filtered(
            lambda l, p=product_id: l.product_id.id == product_id
        )

    def _prepare_cart_item(self, params, cart):
        return {
            "product_id": params["product_id"],
            "product_uom_qty": params["item_qty"],
            "order_id": cart.id,
        }

    def _load_target_email(self, record_id):
        """
        As this service doesn't have a _expose_model, we have to do it manually
        :param record_id: int
        :return: record or None
        """
        return self.env["sale.order"].browse(record_id)

    def _get_openapi_default_parameters(self):
        defaults = super(CartService, self)._get_openapi_default_parameters()
        defaults.append(
            {
                "name": "SESS-CART-ID",
                "in": "header",
                "description": "Session Cart Identifier",
                "required": False,
                "schema": {"type": "integer"},
                "style": "simple",
            }
        )
        return defaults
