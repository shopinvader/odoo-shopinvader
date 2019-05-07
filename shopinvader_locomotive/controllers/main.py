# -*- coding: utf-8 -*-
# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo.addons.shopinvader.controllers.main import InvaderController
from odoo.http import request

_logger = logging.getLogger(__name__)


class LocomotiveInvaderController(InvaderController):
    @classmethod
    def _get_client_header(cls, headers):
        res = {}
        for key, val in headers.items():
            if key.upper().startswith("HTTP_INVADER_CLIENT_"):
                res[key.replace("HTTP_INVADER_CLIENT_", "")] = val
        return res

    def _get_component_context(self):
        res = super(LocomotiveInvaderController, self)._get_component_context()
        headers = request.httprequest.environ
        res["client_header"] = self._get_client_header(headers)
        return res
