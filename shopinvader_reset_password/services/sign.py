# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.addons.shopinvader.services.sign import SignService
from openerp.addons.shopinvader.backend import shopinvader
from datetime import datetime


@shopinvader(replacing=SignService)
class SignService(SignService):

    def _assign_cart_and_get_store_cache(self):
        res = super(SignService, self)._assign_cart_and_get_store_cache()
        shop_partner = self.env['shopinvader.partner'].search([
            ('backend_id', '=', self.backend_record.id),
            ('record_id', '=', self.partner.id),
            ])
        if not shop_partner.date_initialisation:
            shop_partner.date_initialisation = datetime.now()
        return res
