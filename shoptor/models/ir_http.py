# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, exceptions
from openerp.http import request
import logging

_logger = logging.getLogger(__name__)


class IrHttp(models.Model):
    _inherit = 'ir.http'

    def _auth_method_shoptor(self):
        if request.params.get('api_key'):
            backend_id = self.pool['locomotivecms.backend'].search(
                request.cr, 1,
                [('odoo_api', '=', request.params['api_key'])])
            if len(backend_id) == 1:
                request.backend_id = backend_id[0]
                request.uid = 1
                request.email = None
                request.partner_id = None
                return True
        _logger.warning("Wrong Api key, access denied")
        raise exceptions.AccessDenied()
