# -*- coding: utf-8 -*-
# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import http
from openerp.http import request
from .main import rjson


class PartnerController(http.Controller):

    @http.route('/shoptor/contacts', methods=['GET'], auth="none")
    def list(self, session=None, email=None, contact_type=None):
        if contact_type and contact_type not in ['profile', 'address']:
            # TODO raise correctly
            raise "invalid contact_type"
        partner_id = 13470
        result = []
        partner = request.env['res.partner'].sudo().browse(partner_id)
        if not contact_type or contact_type == 'profile':
            result += partner.to_json_contact()
        if not contact_type or contact_type == 'address':
            result += partner.child_ids.to_json_contact()
        return rjson(result)

    @http.route('/shoptor/contacts', methods=['POST'], auth="none")
    def create(self, **params):
        # TODO check params and getting the partner
        params['name'] = params.get('firstname', '')\
            + params.get('lastname', '')
        params['parent_id'] = 13470
        partner = request.env['res.partner'].sudo().create(params)
        return rjson(partner.to_json_contact())

    @http.route('/shoptor/contacts/<partner_id>', methods=['PUT'], auth="none")
    def edit(self, partner_id, **params):
        # TODO check params
        params['parent_id'] = 13470
        params['name'] = params.get('firstname', '')\
            + params.get('lastname', '')
        partner = request.env['res.partner'].sudo().browse(int(partner_id))
        partner.write(params)
        return rjson(partner.to_json_contact())

    @http.route('/shoptor/contacts/<partner_id>',
                methods=['DELETE'], auth="none")
    def delete(self, partner_id):
        # TODO check params
        return request.env['res.partner'].sudo()\
            .browse(int(partner_id)).unlink()
