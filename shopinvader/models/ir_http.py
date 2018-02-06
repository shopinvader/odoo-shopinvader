# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.http import request

from odoo import models


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _extract_shopinvader_session(cls, headers):
        # HTTP_SESS are data that are store in the shopinvader session
        # and forwarded to odoo at each request
        # it allow to access to some specific field of the user session
        # By security always force typing
        # Note: rails cookies store session are serveless ;)
        return {
            'cart_id': int(headers.get('HTTP_SESS_CART_ID', 0))
            }

    @classmethod
    def _auth_method_shopinvader(cls):
        ret = super(IrHttp, cls)._auth_method_shopinvader()
        headers = request.httprequest.environ
        request.shopinvader_session = cls._extract_shopinvader_session(headers)
        return ret
