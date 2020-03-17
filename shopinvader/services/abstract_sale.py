# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo.addons.component.core import AbstractComponent

_logger = logging.getLogger(__name__)


class AbstractSaleService(AbstractComponent):
    _inherit = "shopinvader.abstract.mail.service"
    _name = "shopinvader.abstract.sale.service"

    def _convert_one_sale(self, sale):
        sale.ensure_one()
        state_label = self._get_selection_label(sale, "shopinvader_state")
        return {
            "id": sale.id,
            "state": sale.shopinvader_state,
            "state_label": state_label,
            "name": sale.name,
            "date": sale.date_order,
            "client_order_ref": sale.client_order_ref,
            "step": self._convert_step(sale),
            "lines": self._convert_lines(sale),
            "amount": self._convert_amount(sale),
            "shipping": self._convert_shipping(sale),
            "invoicing": self._convert_invoicing(sale),
        }

    def _schema_for_one_sale(self):
        return {
            "id": {"required": True, "type": "integer"},
            # TODO: validate w/ shopinvader_state options
            "state": {"type": "string", "required": True},
            "name": {"type": "string", "required": True},
            # # TODO: shall we use `date` type?
            "date": {"type": "string", "required": True},
            "step": {"type": "dict", "schema": self._schema_for_step()},
            "lines": {"type": "dict", "schema": self._schema_for_lines()},
            "amount": {"type": "dict", "schema": self._schema_for_amount()},
            "shipping": {
                "type": "dict",
                "schema": self._schema_for_shipping(),
            },
            "invoicing": {
                "type": "dict",
                "schema": self._schema_for_invoicing(),
            },
        }

    def _convert_step(self, sale):
        return {
            "current": sale.current_step_id.code,
            "done": sale.done_step_ids.mapped("code"),
        }

    def _schema_for_step(self):
        # TODO: return options
        return {
            "current": {"type": "string", "required": True},
            "done": {
                "type": "list",
                "schema": {"type": "string"},
                "nullable": True,
            },
        }

    def _convert_lines(self, sale):
        items = []
        for line in sale.order_line:
            if self._is_item(line):
                items.append(self._convert_one_line(line))
        return {
            "items": items,
            "count": sum([item["qty"] for item in items]),
            "amount": {
                "tax": sum([item["amount"]["tax"] for item in items]),
                "untaxed": sum([item["amount"]["untaxed"] for item in items]),
                "total": sum([item["amount"]["total"] for item in items]),
            },
        }

    def _schema_for_lines(self):
        return {
            "items": {
                "type": "list",
                "schema": {
                    "type": "dict",
                    "schema": self._schema_for_one_line(),
                },
                "nullable": True,
            },
            "count": {"type": "integer"},
            "amount": {
                "type": "dict",
                "schema": {
                    "tax": {"type": "float"},
                    "untaxed": {"type": "float"},
                    "total": {"type": "float"},
                },
            },
        }

    def _convert_one_line(self, line):
        variant = line.product_id._get_invader_variant(
            self.shopinvader_backend, self.env.context.get("lang")
        )
        if not variant:
            _logger.debug(
                "No variant found with ctx lang `%s`. "
                "Falling back to partner lang `%s",
                self.env.context.get("lang"),
                line.order_id.partner_id.lang,
            )
            # this likely should never happen if the request from client
            # is forwarded properly
            variant = line.product_id._get_invader_variant(
                self.shopinvader_backend, line.order_id.partner_id.lang
            )
        if variant:
            # TODO we should reuse the parser of the index
            product = variant.jsonify(self._parser_product())[0]
        else:
            product = {}
        return {
            "id": line.id,
            "product": product,
            "amount": {
                "price": line.price_unit,
                "untaxed": line.price_subtotal,
                "tax": line.price_tax,
                "total": line.price_total,
                "total_without_discount": line.price_total_no_discount,
            },
            "qty": line.product_uom_qty,
            "discount": {"rate": line.discount, "value": line.discount_total},
        }

    def _parser_product(self):
        return [
            "full_name:name",
            "short_name",
            ("shopinvader_product_id:model", ("name",)),
            "object_id:id",
            "url_key",
            "default_code:sku",
        ]

    def _schema_for_one_line(self):
        return {
            "id": {"required": True, "type": "integer"},
            "product": {
                "type": "dict",
                "schema": self._schema_for_line_product(),
            },
            "amount": {
                "type": "dict",
                "schema": self._schema_for_line_amount(),
            },
            "qty": {"type": "float"},
            "discount": {
                "type": "dict",
                "schema": {
                    "rate": {"type": "float"},
                    "value": {"type": "float"},
                },
            },
        }

    def _schema_for_line_product(self):
        return {
            "id": {"required": True, "type": "integer"},
            "name": {"required": True, "type": "string"},
            "short_name": {"type": "string"},
            "model": {"type": "string"},
            "url_key": {"type": "string"},
            "sku": {"type": "string"},
        }

    def _schema_for_line_amount(self):
        return {
            "price": {"type": "float"},
            "tax": {"type": "float"},
            "untaxed": {"type": "float"},
            "total": {"type": "float"},
            "total_without_discount": {"type": "float"},
        }

    def _is_item(self, line):
        return True

    def _convert_shipping(self, sale):
        if (
            sale.partner_shipping_id
            == self.shopinvader_backend.anonymous_partner_id
        ):
            return {"address": {}}
        else:
            address_service = self.component(usage="addresses")
            return {
                "address": address_service._to_json(sale.partner_shipping_id)[
                    0
                ]
            }

    def _schema_for_shipping(self):
        return {
            "address": {
                "type": "dict",
                "schema": self.component(
                    usage="addresses"
                )._schema_for_one_address(access_info=False),
            }
        }

    def _convert_invoicing(self, sale):
        if (
            sale.partner_invoice_id
            == self.shopinvader_backend.anonymous_partner_id
        ):
            return {"address": {}}
        else:
            address_service = self.component(usage="addresses")
            return {
                "address": address_service._to_json(sale.partner_invoice_id)[0]
            }

    def _schema_for_invoicing(self):
        return {
            "address": {
                "type": "dict",
                "schema": self.component(
                    usage="addresses"
                )._schema_for_one_address(access_info=False),
            }
        }

    def _convert_amount(self, sale):
        return {
            "tax": sale.amount_tax,
            "untaxed": sale.amount_untaxed,
            "total": sale.amount_total,
            "discount_total": sale.discount_total,
            "total_without_discount": sale.price_total_no_discount,
        }

    def _schema_for_amount(self):
        return {
            "tax": {"type": "float"},
            "untaxed": {"type": "float"},
            "total": {"type": "float"},
            "discount_total": {"type": "float"},
            "total_without_discount": {"type": "float"},
        }

    def _to_json(self, sales):
        res = []
        for sale in sales:
            res.append(self._convert_one_sale(sale))
        return res
