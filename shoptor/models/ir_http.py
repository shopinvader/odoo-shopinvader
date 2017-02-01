# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from werkzeug.exceptions import Unauthorized

from openerp import models
from openerp.http import request
import logging

_logger = logging.getLogger(__name__)


class IrHttp(models.Model):
    _inherit = 'ir.http'

    def _locomotive_get_partner_from_header(self, headers):
        partner_email = headers.get('HTTP_PARTNER_EMAIL')
        if partner_email:
            loco_partner = request.env['locomotive.partner'].search([
                ('backend_id', '=', request.backend.id),
                ('partner_email', '=', partner_email),
                ])
            if loco_partner:
                return loco_partner.record_id
            else:
                _logger.error("Wrong HTTP_PARTNER_EMAIL")
                raise Unauthorized("Wrong HTTP_PARTNER_EMAIL")
        return None

    def _auth_method_shoptor(self):
        headers = request.httprequest.environ
        print headers
        if headers.get('HTTP_API_KEY'):
            request.uid = 1
            backend = request.env['locomotive.backend'].search(
                [('odoo_api', '=', headers['HTTP_API_KEY'])])
            if len(backend) == 1:
                request.backend = backend
                request.partner = self._locomotive_get_partner_from_header(headers)
                return True
        _logger.error("Wrong HTTP_API_KEY, access denied")
        raise Unauthorized("Wrong HTTP_API_KEY, access denied")
