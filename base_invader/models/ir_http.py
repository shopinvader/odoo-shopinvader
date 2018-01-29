# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo.http import request
from odoo import models
from werkzeug.exceptions import Unauthorized


_logger = logging.getLogger(__name__)


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _auth_method_api_key(cls):
        headers = request.httprequest.environ
        api_key = headers.get('HTTP_API_KEY')
        if api_key:
            if headers.get('HTTP_LANG'):
                request.context = {'lang': headers['HTTP_LANG']}
            request.uid = 1
            backend = request.env['invader.entrypoint'].search(
                [('api_key', '=', api_key)])
            if len(backend) == 1:
                request.backend = backend
                return True
        _logger.error("Wrong HTTP_API_KEY, access denied")
        raise Unauthorized("Access denied")
