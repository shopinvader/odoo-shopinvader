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


class ShoptorController(Controller):

    def send_to_service(self, service_class, params):
        method = request.httprequest.method
        service = self._get_service(service_class)
        if method == 'GET':
            if 'id' in params:
                res = service.get(params)
            else:
                res = service.list(params)
        elif method == 'POST':
            res = service.create(params)
        elif method == 'PUT':
            res = service.update(params)
        elif method == 'DELETE':
            res = service.delete(params)
        return request.make_response(res)

    def _get_service(self, service_class):
        model_name = service_class._model_name
        session = ConnectorSession.from_env(request.env)
        env = get_environment(session, model_name, request.backend.id)
        service = env.backend.get_class(service_class, session, model_name)
        return service(env, request.partner)

    # Cart

    @route('/shoptor/cart', methods=['GET'], auth="shoptor")
    def cart_list(self, **params):
        return self.send_to_service(CartService, params)

    @route('/shoptor/cart/<id>', methods=['GET', 'PUT'],
           auth="shoptor")
    def cart(self, **params):
        return self.send_to_service(CartService, params)

    # Cart Item

    @route('/shoptor/cart/item', methods=['POST', 'PUT', 'DELETE'],
           auth="shoptor")
    def item(self, **params):
        return self.send_to_service(CartItemService, params)

    # Contact
    @route('/shoptor/contacts', methods=['GET', 'POST'], auth="shoptor")
    def contact(self, **params):
        return self.send_to_service(ContactService, params)

    @route('/shoptor/contacts/<id>', methods=['PUT', 'DELETE'],
           auth="shoptor")
    def contact_update_delete(self, **params):
        return self.send_to_service(ContactService, params)

    # Customer

    @route('/shoptor/customer', methods=['POST'], auth="shoptor")
    def customer(self, **params):
        return self.send_to_service(CustomerService, params)

    # Order History

    @route('/shoptor/orders', methods=['GET'], auth="none")
    def orders(self, per_page=5, page=1):
        # TODO get the right partner
        partner_id = 13470
        per_page = int(per_page)
        page = int(page)
        result = request.env['sale.order'].sudo().get_order_history(
            partner_id, per_page=per_page, page=page)
        return result
