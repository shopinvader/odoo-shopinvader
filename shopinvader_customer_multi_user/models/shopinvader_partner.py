# Copyright 2019 Camptocamp SA (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ShopinvaderPartner(models.Model):

    _inherit = "shopinvader.partner"

    is_invader_user = fields.Boolean(
        compute="_compute_is_invader_user", store=True
    )

    @api.depends("parent_id", "parent_id.shopinvader_bind_ids")
    def _compute_is_invader_user(self):
        for rec in self:
            rec.is_invader_user = rec._check_is_invader_user()

    def _check_is_invader_user(self):
        """Check if current partner is a bound shopinvader user.

        You have only 2 ways to make a partner a shop customer:

        1. register new account from the client
        2. create a binding for the partner

        If we have a binding on both records (child partner and parent partner)
        this is an invader user.
        """
        return bool(
            self.parent_id.shopinvader_bind_ids.filtered(
                lambda x: x.backend_id == self.backend_id
            )
        )

    @api.model
    def create(self, vals):
        binding = super().create(vals)
        # Generate company's invader user token when creating a binding
        partner = binding.record_id
        if (
            binding.backend_id.customer_multi_user
            and not partner.invader_user_token
            and partner.is_company
        ):
            partner.assign_invader_user_token()
        return binding
