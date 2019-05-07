# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader.controllers.main import InvaderController
from odoo.http import route


class TransactionShopinvaderController(InvaderController):
    @route(
        "/shopinvader/<string:usage>/check_payment/<string:provider_name>",
        methods=["GET", "POST"],
        auth="api_key",
    )
    def check_payment(self, usage, **params):
        return self._process_method(usage, "check_payment", params=params)
