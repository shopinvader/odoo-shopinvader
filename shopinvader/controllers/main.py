# -*- coding: utf-8 -*-
# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo.addons.base_rest.controllers import main
from odoo.http import request

_logger = logging.getLogger(__name__)


class InvaderController(main.RestController):

    _root_path = '/shopinvader/'
    _collection = 'locomotive.backend'
    _default_auth = 'api_key'

    @classmethod
    def _get_partner_from_headers(cls, headers):
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

    @classmethod
    def _get_locomotive_backend_from_request(cls):
        auth_api_key = getattr(request, 'auth_api_key', None)
        backend_model = request.env['locomotive.backend']
        if auth_api_key:
            return backend_model.search([(
                'auth_api_key_id', '=', auth_api_key.id
            )])
        return backend_model.browse([])

    @classmethod
    def _get_shopinvader_session_from_headers(cls, headers):
        # HTTP_SESS are data that are store in the shopinvader session
        # and forwarded to odoo at each request
        # it allow to access to some specific field of the user session
        # By security always force typing
        # Note: rails cookies store session are serveless ;)
        return {
            'cart_id': int(headers.get('HTTP_SESS_CART_ID', 0))
        }

    def _get_component_context(self):
        """
        This method adds the component context:
        * the partner
        * the cart_id
        * the locomotive_backend
        """
        res = super(main.RestController, self)._get_component_context()
        headers = request.httprequest.environ
        res['partner'] = self._get_partner_from_headers(headers)
        res['shopinvader_session'] = \
            self._get_shopinvader_session_from_headers(headers)
        res['locomotive_backend'] = self._get_locomotive_backend_from_request()
        return res
