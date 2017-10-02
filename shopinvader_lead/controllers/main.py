# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.http import route
from odoo.addons.shopinvader.controllers.main import ShopinvaderController
from ..services.lead import LeadService


class ShopinvaderClaimController(ShopinvaderController):

    @route('/shopinvader/lead', methods=['POST'], auth="shopinvader")
    def lead(self, **params):
        return self.send_to_service(LeadService, params)
