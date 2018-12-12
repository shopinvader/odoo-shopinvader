# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.component.core import AbstractComponent, Component
from odoo.exceptions import UserError
from odoo.tools.translate import _
import logging
_logger = logging.getLogger(__name__)


class AbstractSaleService(AbstractComponent):
    _inherit = 'shopinvader.abstract.sale.service'

    def _convert_shipping(self, cart):
        res = super(AbstractSaleService, self)._convert_shipping(cart)
        selected_carrier = {}
        if cart.carrier_id:
            carrier = cart.carrier_id
            selected_carrier = {
                'id': carrier.id,
                'name': carrier.name,
                'description': carrier.description,
            }
        res.update({
            'amount': {
                'tax': cart.shipping_amount_tax,
                'untaxed': cart.shipping_amount_untaxed,
                'total': cart.shipping_amount_total,
                },
            'selected_carrier': selected_carrier,
            })
        return res

    def _prepare_carrier(self, carrier):
        return {
            'id': carrier.id,
            'name': carrier.name,
            'description': carrier.description,
            'price': carrier.price,
            }

    def _get_available_carrier(self, cart):
        return [self._prepare_carrier(carrier)
                for carrier in cart._get_available_carrier()]

    def _is_item(self, line):
        return not line.is_delivery


class CartService(Component):
    _inherit = 'shopinvader.cart.service'

    def get_delivery_methods(self):
        """
            This service will return all possible delivery methods for the
            current cart
        :return:
        """
        cart = self._get()
        return self._get_available_carrier(cart)

    def apply_delivery_method(self, **params):
        """
            This service will apply the given delivery method to the current
            cart
        :param params: Dict containing delivery method to apply
        :return:
        """
        cart = self._get()
        if not cart:
            raise UserError(_('There is not cart'))
        else:
            self._set_carrier(cart, params['carrier']['id'])
            return self._to_json(cart)

    # Validator
    def _validator_apply_delivery_method(self):
        return {
            'carrier': {
                'type': 'dict',
                'schema': {
                    'id': {
                        'coerce': int,
                        'nullable': True,
                        'required': True,
                        'type': 'integer',
                        },
                    }
                },
            }

    def _validator_get_delivery_methods(self):
        return {}

    def _set_carrier(self, cart, carrier_id):
        if carrier_id not in [
                x['id'] for x in self._get_available_carrier(cart)]:
            raise UserError(
                _('This delivery method is not available for you order'))
        cart.write({'carrier_id': carrier_id})
        cart.delivery_set()
