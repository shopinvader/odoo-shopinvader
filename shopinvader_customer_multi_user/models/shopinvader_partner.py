# Copyright 2019 Camptocamp SA (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ShopinvaderPartner(models.Model):

    _inherit = "shopinvader.partner"

    is_invader_user = fields.Boolean(
        compute="_compute_parent_dependent", store=True
    )
    main_partner_id = fields.Many2one(
        string="Main partner for this account",
        help="The main account for the shop might differ from the one of the user."
        "It's nice to display in the frontend "
        "which account the user belongs to."
        "Usually is the company but depending on the logic "
        "it can be another contact in the hierarchy.",
        comodel_name="shopinvader.partner",
        compute="_compute_parent_dependent",
        store=True,
    )

    @api.depends("parent_id", "parent_id.shopinvader_bind_ids", "backend_id")
    def _compute_parent_dependent(self):
        for rec in self:
            rec.main_partner_id = rec._get_main_partner()
            rec.is_invader_user = rec._check_is_invader_user()

    def _check_is_invader_user(self):
        """Check if current partner is a bound shopinvader user.

        You have only 2 ways to make a partner a shop customer:

        1. register new account from the client
        2. create a binding for the partner

        If we have a binding on both records (child partner and parent partner)
        this is an invader user.
        """
        return bool(self.main_partner_id and not self.main_partner_id == self)

    def _get_parent_partner(self):
        """Get parent bound partner matching backend."""
        return self.parent_id._get_invader_partner(self.backend_id)

    def _get_main_partner(self):
        """Retrieve the main partner of the account."""
        return self._get_company()

    def _get_company(self):
        """Lookup for the company among bound parent records."""
        if self.is_company:
            return self
        partner = self
        while partner._get_parent_partner():
            partner = partner._get_parent_partner()
            if partner.is_company:
                break
        return partner

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
