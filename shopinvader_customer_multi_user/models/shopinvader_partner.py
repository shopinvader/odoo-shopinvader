# Copyright 2019 Camptocamp SA (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class ShopinvaderPartner(models.Model):

    _inherit = "shopinvader.partner"

    @api.model
    def create(self, vals):
        binding = super().create(vals)
        partner = binding.record_id
        if (
            binding.backend_id.customer_multi_user
            and not partner.invader_user_token
            and partner.is_company
        ):
            partner.assign_invader_user_token()
        return binding

    @api.multi
    def is_invader_user(self):
        self.ensure_one()
        return self.record_id.is_invader_user()
