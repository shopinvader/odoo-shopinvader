# -*- coding: utf-8 -*-
# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.http import route
from odoo.addons.shopinvader.controllers.main import ShopinvaderController
import logging

_logger = logging.getLogger(__name__)


class ShopinvaderVatController(ShopinvaderController):

    # Check Vat
    @route('/shopinvader/check_vat', methods=['GET'], auth="shopinvader")
    def check_vat(self, **params):
        return self.send_to_service('check.vat.service', params)
