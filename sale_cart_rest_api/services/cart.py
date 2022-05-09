# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import uuid

import pytz

from odoo import fields
from odoo.tools.float_utils import float_round

from odoo.addons.base_rest import restapi
from odoo.addons.base_rest.components.service import to_int
from odoo.addons.component.core import Component


class CartService(Component):
    """Sale Cart API.

    The indent of this new api is to provide lightweight services layer
    on top of the sale.order model used by the shopinvader-js-cart
    library to manage cart operations

    The service is designed to work with authenticated or anonymous users.
    The logic to retrieve the cart will defer depending if the user
    is authenticated or not?

     If user is authenticated:
            If uuid:
                -> try to find cart for given uuid and user
            Else
                -> try to find cart for given user
            -> if no cart => create empty cart
            return cart
        If anonymous:
            If uuid:
                -> try to find cart for given uuid and anonymous user
            Else
                -> create empty cart
            return cart

    Cart retrieval is based on a provided UUID not on the odoo id. The indent
    is to allow the development of a layer between the js frontend and odoo
    acting as a buffer and able to manage the carts even if odoo is temporarily
    unavailable.
    """

    _inherit = "base.rest.service"
    _name = "sale.cart.service"
    _usage = "cart"

    @restapi.method(
        [(["/"], "GET")],
        input_param=restapi.CerberusValidator("_get_input_schema"),
        output_param=restapi.CerberusValidator("_cart_schema"),
        auth="public_or_default",
    )
    def get(self, uuid=None):
        """Get current cart for the given UUID if provided.

        If no cart is found the response is an empty document
        """
        cart = self._find_open_cart(uuid)
        return self._response_for_cart(cart)

    @restapi.method(
        [(["/sync"], "POST")],
        input_param=restapi.CerberusValidator("_sync_input_schema"),
        output_param=restapi.CerberusValidator("_cart_schema"),
        auth="public_or_default",
    )
    def sync(self, uuid=None, transactions=None):
        """If no cart is found and no transactions is provided into the
        request the response is an empty json object."""
        cart = self._find_open_cart(uuid)
        if not cart and transactions:
            cart = self._create_empty_cart()
        if not uuid or cart.uuid == uuid:
            # only apply transaction to a cart if:
            # * no uuid -> new cart
            # * uuid = cart.uuid: Existing cart and transaction for this cart
            cart._apply_transactions(transactions)
        return self._response_for_cart(cart)

    # #######
    # schemas
    # #######
    def _get_input_schema(self):
        return {
            "uuid": {"type": "string", "required": False, "nullable": True}
        }

    def _sync_input_schema(self):
        return {
            "uuid": {"type": "string", "required": False, "nullable": True},
            "transactions": {
                "type": "list",
                "schema": {
                    "type": "dict",
                    "schema": {
                        "uuid": {
                            "type": "string",
                            "required": False,
                            "nullable": True,
                        },
                        "qty": {
                            "coerce": float,
                            "required": True,
                            "type": "float",
                        },
                        "product_id": {
                            "coerce": to_int,
                            "nullable": False,
                            "required": True,
                            "type": "integer",
                        },
                    },
                },
            },
        }

    def _cart_schema(self):
        return {
            "uuid": {"type": "string", "required": False, "nullable": True},
            "id": {"type": "integer", "required": True, "nullable": False},
            "state": {"type": "string", "required": True, "nullable": False},
            "state_label": {
                "type": "string",
                "required": True,
                "nullable": False,
            },
            "name": {"type": "string", "required": True, "nullable": False},
            "date": {"type": "datetime", "required": True, "nullable": False},
            "lines": {
                "type": "list",
                "schema": {"type": "dict", "schema": self._line_output_schema},
                "required": True,
                "nullable": True,
            },
            "amount": {"type": "dict", "schema": self._amount_output_schema},
            "delivery": {
                "type": "dict",
                "schema": self._delivery_output_schema,
                "required": False,
                "nullable": True,
            },
            "invoicing": {
                "type": "dict",
                "schema": self._invoicing_output_schema,
                "required": False,
                "nullable": True,
            },
            "note": {"type": "string", "required": False, "nullable": True},
        }

    @property
    def _delivery_output_schema(self):
        return {
            "address": {
                "type": "dict",
                "schema": self.partner_serializer._json_address_schema,
                "required": False,
                "nullable": True,
            }
        }

    @property
    def _invoicing_output_schema(self):
        return {
            "address": {
                "type": "dict",
                "schema": self.partner_serializer._json_address_schema,
                "required": False,
                "nullable": True,
            }
        }

    @property
    def _line_output_schema(self):
        return {
            "id": {"type": "integer", "required": True, "nullable": False},
            "product_id": {
                "type": "integer",
                "required": True,
                "nullable": True,
            },
            "name": {"type": "string", "required": True, "nullable": False},
            "amount": {
                "type": "dict",
                "schema": self._amount_with_price_output_schema,
            },
            "qty": {"type": "float", "required": True, "nullable": False},
        }

    @property
    def _amount_output_schema(self):
        return {
            "tax": {"type": "float", "required": True, "nullable": False},
            "untaxed": {"type": "float", "required": True, "nullable": False},
            "total": {"type": "float", "required": True, "nullable": False},
            "discount_total": {
                "type": "float",
                "required": True,
                "nullable": False,
            },
            "total_without_discount": {
                "type": "float",
                "required": True,
                "nullable": False,
            },
        }

    @property
    def _amount_with_price_output_schema(self):
        amount_schema = self._amount_output_schema
        amount_schema["price"] = {
            "type": "float",
            "required": True,
            "nullable": False,
        }
        return amount_schema

    # ##############
    # implementation
    # ##############

    @property
    def partner_serializer(self):
        return self.env["res.partner.serializer"]

    @property
    def anonymous_partner(self):
        return self.env.ref("base.public_user").partner_id

    def _get_open_cart_domain(self, uuid=None):
        partner = self.authenticated_partner or self.anonymous_partner
        domain = [
            ("typology", "=", "cart"),
            ("state", "=", "draft"),
            ("partner_id", "=", partner.id),
        ]
        if uuid:
            domain.append(("uuid", "=", uuid))
        return domain

    def _find_open_cart(self, uuid=None):
        if not self.authenticated_partner and not uuid:
            # uuid is required for anonymous users
            return self.env["sale.order"].browse()
        domain = self._get_open_cart_domain(uuid=uuid)
        cart = self.env["sale.order"].search(domain, limit=1)
        if not cart and self.authenticated_partner and uuid:
            # maybe a current cart exists with another uuid
            domain = self._get_open_cart_domain(uuid=None)
            cart = self.env["sale.order"].search(domain, limit=1)
        return cart

    def _response_for_cart(self, cart):
        if cart:
            return self._convert_cart_to_json(cart)
        # IF no cart, return a RESPONSE object to avoid validation
        headers = {"Content-Type": "application/json"}
        return self.request.make_response("{}", headers=headers)

    def _prepare_cart(self):
        partner = self.authenticated_partner or self.anonymous_partner
        vals = {
            "uuid": str(uuid.uuid4()),
            "typology": "cart",
            "partner_id": partner.id,
        }
        vals.update(self.env["sale.order"].play_onchanges(vals, vals.keys()))
        if not vals.get("pricelist_id"):
            vals["pricelist_id"] = self._get_default_pricelist_id()
        return vals

    def _get_default_pricelist_id(self):
        """ Return the pricelist to use if no one found on the partner

        By default we return the one defined on the anonymous user partner.
        Since the anonymous partner is inactive, we must disable the active test
        to be able to read the property product pricelist
        """
        return (
            self.env.ref("base.public_user")
            .partner_id.with_context(active_test=False)
            .property_product_pricelist.id
        )

    def _create_empty_cart(self):
        vals = self._prepare_cart()
        return self.env["sale.order"].create(vals)

    def _convert_cart_to_json(self, sale):
        state_label = self._get_selection_label(sale, "state")
        return {
            "id": sale.id,
            "uuid": sale.uuid or None,
            "state": sale.state,
            "state_label": state_label or None,
            "name": sale.name,
            "date": self._odoo_str_dt_to_dt_utc(sale.date_order),
            "lines": self._convert_lines(sale),
            "amount": self._convert_amount(sale),
            "delivery": self._convert_delivery(sale),
            "invoicing": self._convert_invoicing(sale),
            "note": sale.note or None,
        }

    def _convert_one_line(self, line):
        return {
            "id": line.id,
            "product_id": line.product_id.id,
            "name": line.name or None,
            "amount": {
                "price": line.price_unit,
                "untaxed": line.price_subtotal,
                "tax": line.price_tax,
                "total": line.price_total,
                "discount_total": line.discount_total,
                "total_without_discount": line.price_total_no_discount,
            },
            "qty": line.product_uom_qty,
            "discount": {"rate": line.discount, "value": line.discount_total},
        }

    def _convert_lines(self, sale):
        lines = []
        for line in sale.order_line:
            if self._is_line(line):
                lines.append(self._convert_one_line(line))
        return lines

    def _convert_delivery(self, sale):
        delivery = {}
        if sale.partner_shipping_id != self.anonymous_partner:
            delivery["address"] = self.partner_serializer._to_json_address(
                sale.partner_shipping_id
            )
        return delivery

    def _convert_invoicing(self, sale):
        invoicing = {}
        if sale.partner_invoice_id != self.anonymous_partner:
            invoicing["address"] = self.partner_serializer._to_json_address(
                sale.partner_invoice_id
            )
        return invoicing

    def _convert_amount(self, sale):
        precision = sale.currency_id.decimal_places
        return {
            "tax": float_round(sale.amount_tax, precision),
            "untaxed": float_round(sale.amount_untaxed, precision),
            "total": float_round(sale.amount_total, precision),
            "discount_total": float_round(sale.discount_total, precision),
            "total_without_discount": float_round(
                sale.price_total_no_discount, precision
            ),
        }

    def _is_line(self, line):
        return True

    def _get_selection_label(self, record, field):
        """
        Get the translated label of the record selection field
        :param record: recordset
        :param field: str
        :return: str
        """
        if field not in record._fields:
            return ""
        # convert_to_export(...) give the label of the selection (translated).
        return record._fields.get(field).convert_to_export(
            record[field], record
        )

    def _odoo_str_dt_to_dt_utc(self, value_str):
        if not value_str:
            return None
        dt = fields.Datetime.from_string(value_str)
        return pytz.utc.localize(dt, is_dst=False)
