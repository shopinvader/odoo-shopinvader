# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
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

    def _convert_step(self, sale):
        return {
            "current": sale.current_step_id.code,
            "done": sale.done_step_ids.mapped("code"),
        }

    def _is_item(self, line):
        return True

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
        product = self._convert_one_line_product(variant)
        return {
            "id": line.id,
            "name": line.name,
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

    def _convert_one_line_product(self, variant):
        return variant.get_shop_data() if variant else {}

    def _convert_lines(self, sale):
        items = []
        for line in sale.order_line:
            if self._is_item(line):
                items.append(self._convert_one_line(line))
        return {
            "items": items,
            # TODO: does this make any sense? Sum up qty of different products?
            "count": sum([item["qty"] for item in items]),
            "amount": {
                "tax": sum([item["amount"]["tax"] for item in items]),
                "untaxed": sum([item["amount"]["untaxed"] for item in items]),
                "total": sum([item["amount"]["total"] for item in items]),
            },
        }

    def _convert_shipping(self, sale):
        if sale.partner_shipping_id == self.shopinvader_backend.anonymous_partner_id:
            return {"address": {}}
        else:
            address_service = self.component(usage="addresses")
            return {"address": address_service._to_json(sale.partner_shipping_id)[0]}

    def _convert_invoicing(self, sale):
        if sale.partner_invoice_id == self.shopinvader_backend.anonymous_partner_id:
            return {"address": {}}
        else:
            address_service = self.component(usage="addresses")
            return {"address": address_service._to_json(sale.partner_invoice_id)[0]}

    def _convert_amount(self, sale):
        return {
            "tax": sale.amount_tax,
            "untaxed": sale.amount_untaxed,
            "total": sale.amount_total,
            "discount_total": sale.discount_total,
            "total_without_discount": sale.price_total_no_discount,
        }

    def _to_json(self, sales, **kw):
        res = []
        for sale in sales:
            res.append(self._convert_one_sale(sale))
        return res
