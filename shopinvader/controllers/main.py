# -*- coding: utf-8 -*-
# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.http import Controller, request, route
# TODO migrate
# from odoo.addons.connector.session import ConnectorSession
# from odoo.addons.connector_locomotivecms.connector import get_environment
from ..services.cart import CartService
from ..services.cart_item import CartItemService
from ..services.address import AddressService
from ..services.customer import CustomerService
from ..services.sale import SaleService
from ..services.sign import SignService
from ..services.transaction import TransactionService
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)


class ShopinvaderController(Controller):

    def send_to_service(self, service_name, params):
        with request.backend.work_on(
                model_name='locomotive.backend',
                partner=request.partner,
                shopinvader_session=request.shopinvader_session) as work:
            service = work.component(usage=service_name)
            start = datetime.now()
            method = request.httprequest.method
            if method == 'GET':
                res = service.get(params)
            elif method == 'POST':
                res = service.create(params)
            elif method == 'PUT':
                res = service.update(params)
            elif method == 'DELETE':
                res = service.delete(params)
            res = request.make_response(res)
            _logger.info('Shopinvader Response in %s', datetime.now() - start)
            return res

    # Cart
    @route('/shopinvader/cart', methods=['GET', 'PUT'], auth="shopinvader")
    def cart_list(self, **params):
        return self.send_to_service(CartService, params)

    # Cart Item
    @route('/shopinvader/cart/item', methods=['POST', 'PUT', 'DELETE'],
           auth="shopinvader")
    def item(self, **params):
        return self.send_to_service(CartItemService, params)

    # Address
    @route('/shopinvader/addresses',
           methods=['GET', 'POST'], auth="shopinvader")
    def address(self, **params):
        return self.send_to_service('address.service', params)

    @route('/shopinvader/addresses/<id>', methods=['PUT', 'DELETE'],
           auth="shopinvader")
    def address_update_delete(self, **params):
        return self.send_to_service(AddressService, params)

    # Customer
    @route('/shopinvader/customer',
           methods=['GET'], auth="shopinvader")
    def customer(self, **params):
        return self.send_to_service(CustomerService, params)

    # Order History
    @route('/shopinvader/sales', methods=['GET'], auth="shopinvader")
    def sale_list(self, **params):
        return self.send_to_service(SaleService, params)

    @route('/shopinvader/sales/<id>', methods=['GET'], auth="shopinvader")
    def sale(self, **params):
        return self.send_to_service(SaleService, params)

    # Check Transaction
    @route('/shopinvader/check_transaction',
           methods=['GET'], auth="shopinvader")
    def check_transaction(self, **params):
        return self.send_to_service(TransactionService, params)

    # Sign action
    @route('/shopinvader/sign',
           methods=['GET', 'PUT', 'POST'], auth="shopinvader")
    def sign(self, **params):
        return self.send_to_service(SignService, params)
