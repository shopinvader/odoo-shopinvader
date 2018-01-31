# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo.http import request

from odoo import models

_logger = logging.getLogger(__name__)


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _get_partner_domain(cls, headers):
        partner_email = headers.get('HTTP_PARTNER_EMAIL')
        if partner_email:
            return [
                ('email', '=', partner_email),
            ]
        return []

    @classmethod
    def _invader_get_partner_from_header(cls, headers):
        partner_domin = cls._get_partner_domain(headers)
        partner_model = request.env[
            request.backend.partner_model_id.model]
        if partner_domin:
            partner = partner_model.search(partner_domin)
            if len(partner) == 1:
                return partner
            else:
                _logger.warning("Wrong HTTP_PARTNER_EMAIL, header ignored")
                if len(partner) > 1:
                    _logger.warning(
                        "More than one %s found for domain: %s",
                        request.backend.partner_model_id.name,
                        partner_domin
                    )
        return partner_model.browse([])

    @classmethod
    def _auth_method_api_key(cls):
        ret = super(IrHttp, cls)._auth_method_api_key()
        headers = request.httprequest.environ
        request.partner =\
           cls._invader_get_partner_from_header(headers)
        return ret
