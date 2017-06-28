# -*- coding: utf-8 -*-
# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.http import Controller, request, route
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.connector_locomotivecms.connector import get_environment
from ..services.cart import CartService
from ..services.cart_item import CartItemService
from ..services.contact import ContactService
from ..services.customer import CustomerService
from ..services.sale import SaleService
from ..services.check_vat import CheckVatService
from ..services.register_anonymous import RegisterAnonymousService
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)


class ShopinvaderController(Controller):

    def send_to_service(self, service_class, params):
        start = datetime.now()
        method = request.httprequest.method
        service = self._get_service(service_class)
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

    def _get_service(self, service_class):
        model_name = service_class._model_name
        session = ConnectorSession.from_env(request.env)
        env = get_environment(session, model_name, request.backend.id)
        service = env.backend.get_class(service_class, session, model_name)
        return service(env, request.partner, request.shopinvader_session)

    # Check Vat
    @route('/shopinvader/check_vat', methods=['GET'], auth="shopinvader")
    def check_vat(self, **params):
        return self.send_to_service(CheckVatService, params)

    # Cart
    @route('/shopinvader/cart', methods=['GET', 'PUT'], auth="shopinvader")
    def cart_list(self, **params):
        return self.send_to_service(CartService, params)

    # Cart Item
    @route('/shopinvader/cart/item', methods=['POST', 'PUT', 'DELETE'],
           auth="shopinvader")
    def item(self, **params):
        return self.send_to_service(CartItemService, params)

    # Contact
    @route('/shopinvader/contacts',
           methods=['GET', 'POST'], auth="shopinvader")
    def contact(self, **params):
        return self.send_to_service(ContactService, params)

    @route('/shopinvader/contacts/<id>', methods=['PUT', 'DELETE'],
           auth="shopinvader")
    def contact_update_delete(self, **params):
        return self.send_to_service(ContactService, params)

    # Customer
    @route('/shopinvader/customer',
           methods=['POST', 'GET'], auth="shopinvader")
    def customer(self, **params):
        return self.send_to_service(CustomerService, params)

    # Anonymous Customer
    @route('/shopinvader/anonymous/register',
           methods=['POST'], auth="shopinvader")
    def anonymous_register(self, **params):
        return self.send_to_service(RegisterAnonymousService, params)

    # Order History
    @route('/shopinvader/orders', methods=['GET'], auth="shopinvader")
    def sale_list(self, **params):
        return self.send_to_service(SaleService, params)

    @route('/shopinvader/orders/<id>', methods=['GET'], auth="shopinvader")
    def sale(self, **params):
        return self.send_to_service(SaleService, params)
