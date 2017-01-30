# -*- coding: utf-8 -*-
# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import http
from openerp.http import request
from .main import rjson, ShoptorController
from ..services.contact import ContactService


class ContactController(ShoptorController):

    @http.route('/shoptor/contacts', methods=['GET', 'POST'], auth="shoptor")
    @http.route('/shoptor/contacts/<partner_id>', methods=['PUT', 'DELETE'],
                auth="shoptor")
    def contact(self, **params):
        method = request.httprequest.method
        contact = self._get_service(ContactService)
        if method == 'GET':
            res = contact.list(params)
        elif method == 'POST':
            res = contact.create(params)
        elif method == 'PUT':
            res = contact.write(params)
        elif method == 'DELETE':
            res = contact.detele(params)
        return rjson(res)
