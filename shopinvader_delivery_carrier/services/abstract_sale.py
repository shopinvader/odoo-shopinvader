# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tools import float_round

from odoo.addons.component.core import AbstractComponent


class AbstractSaleService(AbstractComponent):
    _inherit = "shopinvader.abstract.sale.service"

    def _convert_shipping(self, cart):
        res = super(AbstractSaleService, self)._convert_shipping(cart)
        if cart.carrier_id:
            # we do not need an estimation of the price
            # so we do not pass the cart to the _prepare_carrier method
            # and we remove the field
            selected_carrier = self._prepare_carrier(cart.carrier_id)
            selected_carrier.pop("price")
        else:
            selected_carrier = {}
        res.update(
            {
                "amount": {
                    "tax": cart.shipping_amount_tax,
                    "untaxed": cart.shipping_amount_untaxed,
                    "total": cart.shipping_amount_total,
                },
                "selected_carrier": selected_carrier,
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

    def _prepare_carrier(self, carrier, cart=None):
        service = self.component(usage="delivery_carrier")
        return service._prepare_carrier(carrier, cart=cart)

    def _is_item(self, line):
        return not line.is_delivery and super()._is_item(line)

    def _convert_one_line(self, line):
        # Override to add the qty_delivered
        values = super()._convert_one_line(line)
        values.update({"qty_delivered": line.qty_delivered})
        return values
