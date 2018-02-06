# -*- coding: utf-8 -*-
# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo.addons.base_rest.controllers import main
from odoo.http import request, route

_logger = logging.getLogger(__name__)


class InvaderController(main.RestController):

    @classmethod
    def _get_partner_from_header(cls, headers):
        partner_model = request.env['shopinvader.partner']
        partner_email = headers.get('HTTP_PARTNER_EMAIL')
        if partner_email:
            partner_domain = [
                ('partner_email', '=', partner_email),
            ]
            partner = partner_model.search(partner_domain)
            if len(partner) == 1:
                return partner
            else:
                _logger.warning("Wrong HTTP_PARTNER_EMAIL, header ignored")
                if len(partner) > 1:
                    _logger.warning(
                        "More than one shopinvader.partner found for domain:"
                        " %s", partner_domain
                    )
        return partner_model.browse([])

    def _get_component_context(self):
        """
        This method add the partner into the component context
        """
        res = super(main.RestController, self)._get_component_context()
        headers = request.httprequest.environ
        res['partner'] = self._get_partner_from_header(headers)
        return res

    # Check Vat
    @route('/shopinvader/check_vat', methods=['GET'], auth="shopinvader")
    def check_vat(self, **params):
        return self.send_to_service('check.vat.service', params)

    # Cart
    @route('/shopinvader/cart', methods=['GET', 'PUT'],
           auth="shopinvader", csrf=False)
    def cart_list(self, **params):
        return self.send_to_service('cart.service', params)

    # Cart Item
    @route('/shopinvader/cart/item', methods=['POST', 'PUT', 'DELETE'],
           auth="shopinvader", csrf=False)
    def item(self, **params):
        return self.send_to_service('cart.item.service', params)

    # Address
    @route('/shopinvader/addresses',
           methods=['GET', 'POST'], auth="shopinvader", csrf=False)
    def address(self, **params):
        return self.send_to_service('address.service', params)

    @route('/shopinvader/addresses/<id>', methods=['PUT', 'DELETE'],
           auth="shopinvader", csrf=False)
    def address_update_delete(self, **params):
        return self.send_to_service('address.service', params)

    # Customer
    @route('/shopinvader/customer',
           methods=['GET'], auth="shopinvader")
    def customer(self, **params):
        return self.send_to_service('customer.service', params)

    # Order History
    @route('/shopinvader/sales', methods=['GET'], auth="shopinvader")
    def sale_list(self, **params):
        return self.send_to_service('sale.service', params)

    @route('/shopinvader/sales/<id>', methods=['GET'], auth="shopinvader")
    def sale(self, **params):
        return self.send_to_service('sale.service', params)

    # Sign action
    @route('/shopinvader/sign',
           methods=['GET', 'PUT', 'POST'], auth="shopinvader")
    def sign(self, **params):
        return self.send_to_service('sign.service', params)
