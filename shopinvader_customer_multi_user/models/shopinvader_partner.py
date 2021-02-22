# Copyright 2019 Camptocamp SA (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval


class ShopinvaderPartner(models.Model):

    _inherit = "shopinvader.partner"

    is_invader_user = fields.Boolean(
        compute="_compute_invader_parent_dependent", store=True
    )
    invader_parent_id = fields.Many2one(
        string="Invader parent",
        help="Closest invader partner. "
        "In simple multi-user setup it matches the parent bound partner .",
        comodel_name="shopinvader.partner",
        compute="_compute_invader_parent_dependent",
        store=True,
    )
    main_partner_id = fields.Many2one(
        string="Main partner for this account",
        help="The main account for the shop might differ from the one of the user."
        "It's nice to display in the frontend "
        "which account the user belongs to."
        "Usually is the company but depending on the logic "
        "it can be another contact in the hierarchy.",
        comodel_name="res.partner",
        compute="_compute_main_partner_id",
        store=True,
        readonly=False,
        ondelete="restrict",
    )

    @api.depends("parent_id", "parent_id.shopinvader_bind_ids", "backend_id")
    def _compute_invader_parent_dependent(self):
        for rec in self:
            rec.invader_parent_id = rec._get_invader_parent()
            rec.is_invader_user = rec._check_is_invader_user()

    @api.depends("parent_id", "backend_id")
    def _compute_main_partner_id(self):
        for rec in self:
            rec.main_partner_id = rec._get_main_partner()

    def _check_is_invader_user(self):
        """Check if current partner is a bound shopinvader user.

        You have only 2 ways to make a partner a shop customer:

        1. register new account from the client
        2. create a binding for the partner

        If we have a binding on both records (child partner and parent partner)
        this is an invader user.
        """
        return bool(
            self.invader_parent_id and not self.invader_parent_id == self
        )

    def _get_main_partner(self):
        """Retrieve the main partner of the account."""
        partner = self.parent_id
        main_partner_domain = safe_eval(
            self.backend_id.multi_user_main_partner_domain or "[]"
        )
        if main_partner_domain and partner.filtered_domain(
            main_partner_domain
        ):
            return partner
        while partner.parent_id:
            partner = partner.parent_id
            if main_partner_domain and partner.filtered_domain(
                main_partner_domain
            ):
                return partner
        return partner.filtered_domain(main_partner_domain)

    def _get_parent_invader_parent(self):
        return self.parent_id._get_invader_partner(self.backend_id)

    def _get_invader_parent(self):
        if not self.parent_id:
            return None
        invader_partner = self._get_parent_invader_parent()
        if invader_partner:
            # pick the 1st one
            return invader_partner
        while invader_partner.parent_id:
            invader_partner = invader_partner._get_parent_invader_parent()
            if invader_partner:
                # pick the 1st one in the level up
                break
        return invader_partner

    @api.model
    def create(self, vals):
        binding = super().create(vals)
        main_partner_id = vals.get("main_partner_id")
        if main_partner_id:  # force manual value
            main_partner = self.env["res.partner"].browse(main_partner_id)
            binding.main_partner_id = main_partner
        # Generate company's invader user token when creating a binding
        partner = binding.record_id
        if (
            binding.backend_id.customer_multi_user
            and not partner.invader_user_token
            and partner.is_company
        ):
            partner.assign_invader_user_token()
        return binding
