# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# Copyright 2021 Camptocamp (https://www.camptocamp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tools import float_round

from odoo.addons.component.core import AbstractComponent


class AbstractSaleService(AbstractComponent):
    _inherit = "shopinvader.abstract.sale.service"

    def _convert_shipping(self, cart):
        res = super()._convert_shipping(cart)
        res.update(
            {
                "amount": {
                    "tax": cart.shipping_amount_tax,
                    "untaxed": cart.shipping_amount_untaxed,
                    "total": cart.shipping_amount_total,
                },
                "selected_carrier": (
                    cart.carrier_id.jsonify(self._json_parser_carrier(), one=True)
                    if cart.carrier_id
                    else {}
                ),
            }
        )
        return res

    def _convert_amount(self, sale):
        # Override to add amounts without shipping
        result = super()._convert_amount(sale)
        result.update(
            {
                "tax_without_shipping": sale.item_amount_tax,
                "untaxed_without_shipping": sale.item_amount_untaxed,
                "total_without_shipping": sale.item_amount_total,
                "total_without_shipping_without_discount": float_round(
                    sale.item_amount_total - sale.discount_total,
                    sale.currency_id.decimal_places,
                ),
            }
        )
        return result

    def _is_item(self, line):
        return not line.is_delivery and super()._is_item(line)

    def _convert_one_line(self, line):
        # Override to add the qty_delivered
        values = super()._convert_one_line(line)
        values.update({"qty_delivered": line.qty_delivered})
        return values

    def _json_parser_carrier(self):
        return self.component(usage="delivery_carrier")._json_parser_carrier
