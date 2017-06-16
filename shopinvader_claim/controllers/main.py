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

    @route('/shopinvader/claim/subjects', methods=['GET'], auth="shopinvader")
    def claim_subject(self, **params):
        return self.send_to_service(ClaimSubjectService, params)

    @route('/shopinvader/claims/<id>', methods=['PUT'],
           auth="shopinvader")
    def claim_messages(self, **params):
        return self.send_to_service(ClaimService, params)
