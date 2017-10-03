# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from werkzeug.exceptions import Unauthorized

from odoo import models
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _shopinvader_get_partner_from_header(self, headers):
        partner_email = headers.get('HTTP_PARTNER_EMAIL')
        if partner_email:
            loco_partner = request.env['shopinvader.partner'].search([
                ('backend_id', '=', request.backend.id),
                ('partner_email', '=', partner_email),
                ])
            if loco_partner:
                return loco_partner.record_id
            else:
                _logger.warning("Wrong HTTP_PARTNER_EMAIL, header ignored")
        return None

    @classmethod
    def _extract_shopinvader_session(self, headers):
        # HTTP_SESS are data that are store in the shopinvader session
        # and forwarded to odoo at each request
        # it allow to access to some specific field of the user session
        # By security always force typing
        # Note: rails cookies store session are serveless ;)
        return {
            'cart_id': int(headers.get('HTTP_SESS_CART_ID', 0))
            }

    @classmethod
    def _auth_method_shopinvader(self):
        headers = request.httprequest.environ
        headers['HTTP_API_KEY'] = 'odooapi'
        headers['HTTP_PARTNER_EMAIL'] = 'agrolait@yourcompany.example.com'
        if headers.get('HTTP_API_KEY'):
            request.uid = 1
            backend = request.env['locomotive.backend'].search(
                [('odoo_api', '=', headers['HTTP_API_KEY'])])
            if len(backend) == 1:
                request.backend = backend
                request.partner =\
                    self._shopinvader_get_partner_from_header(headers)
                if headers.get('HTTP_LANG'):
                    request.context['lang'] = headers['HTTP_LANG']
                    request.env = request.env(context=request.context)
                request.shopinvader_session =\
                    self._extract_shopinvader_session(headers)
                return True
        _logger.error("Wrong HTTP_API_KEY, access denied")
        raise Unauthorized("Wrong HTTP_API_KEY, access denied")
