# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com)
# Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.http import route
from openerp.addons.shopinvader.controllers.main import ShopinvaderController
from ..services.claim import ClaimService, ClaimSubjectService


class ShopinvaderClaimController(ShopinvaderController):

    @route('/shopinvader/claims', methods=['GET', 'POST'], auth="shopinvader")
    def claim(self, **params):
        return self.send_to_service(ClaimService, params)

    @route('/shopinvader/claim_subjects', methods=['GET'], auth="shopinvader")
    def claim(self, **params):
        return self.send_to_service(ClaimSubjectService, params)
