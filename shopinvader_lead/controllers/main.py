# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.shopinvader.controllers.main import InvaderController
from odoo.http import route

from ..services.lead import LeadService


class InvaderClaimController(InvaderController):
    @route("/shopinvader/lead", methods=["POST"], auth="shopinvader")
    def lead(self, **params):
        return self.send_to_service(LeadService, params)
