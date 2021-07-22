# Copyright 2019 Camptocamp SA (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval


class ShopinvaderPartner(models.Model):

    _inherit = "shopinvader.partner"

    is_invader_user = fields.Boolean(
        string="Is simple user",
        help="This shop user is not a main profile user",
        compute="_compute_invader_parent_dependent",
        store=True,
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
    is_main_account = fields.Boolean(compute="_compute_is_main_account")
    can_manage_users = fields.Boolean(help="Authorize this user to manage the account.")
    is_admin_account = fields.Boolean(compute="_compute_permission_flags")
    is_users_manager = fields.Boolean(compute="_compute_permission_flags")

    @api.depends("parent_id", "parent_id.shopinvader_bind_ids", "backend_id")
    def _compute_invader_parent_dependent(self):
        for rec in self:
            rec.invader_parent_id = rec._get_invader_parent()
            rec.is_invader_user = rec._check_is_invader_user()

    @api.depends("parent_id", "backend_id")
    def _compute_main_partner_id(self):
        for rec in self:
            rec.main_partner_id = rec._get_main_partner()
            rec.is_main_account = rec.record_id == rec.main_partner_id

    @api.depends("main_partner_id")
    def _compute_is_main_account(self):
        for rec in self:
            rec.is_main_account = rec.record_id == rec.main_partner_id

    @api.depends("parent_id", "can_manage_users")
    def _compute_permission_flags(self):
        for rec in self:
            is_admin = not rec.parent_id
            rec.update(
                {
                    "is_admin_account": is_admin,
                    "is_users_manager": is_admin or rec.can_manage_users,
                }
            )

    def _check_is_invader_user(self):
        """Check if current partner is a bound shopinvader user.

        You have only 2 ways to make a partner a shop customer:

        1. register new account from the client
        2. create a binding for the partner

        If we have a binding on both records (child partner and parent partner)
        this is an invader user.
        """
        return bool(self.invader_parent_id and not self.invader_parent_id == self)

    def _get_main_partner(self):
        """Retrieve the main partner of the account."""
        partner = self.parent_id
        main_partner_domain = safe_eval(
            self.backend_id.multi_user_main_partner_domain or "[]"
        )
        if main_partner_domain and partner.filtered_domain(main_partner_domain):
            return partner
        while partner.parent_id:
            partner = partner.parent_id
            if main_partner_domain and partner.filtered_domain(main_partner_domain):
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
        # Generate company's invader user token when creating a binding
        partner = binding.record_id
        if (
            binding.backend_id.customer_multi_user
            and not partner.invader_user_token
            and partner.is_company
        ):
            partner.assign_invader_user_token()
        return binding

    def _make_partner_domain(self, partner_field, operator="="):
        """Make domain for records related to current shopinvader partner.

        Domain is built considering backend's policy.
        Main users can see all records but simple users
        should be able to see records only from their parents
        and not from sibling users.
        """
        # Main users can always see everything down their hierarchy
        if self.is_admin_account or self.is_main_account:
            return [(partner_field, "child_of", self.record_id.id)]

        # Change partner domain based on backend policy
        policy_field = self.backend_id.multi_user_records_policy
        related_partner = self[policy_field]
        main_account = self.main_partner_id
        # Normally see records owned by the same user
        partner_domains = [[(partner_field, operator, self.record_id.id)]]
        if related_partner and not self.record_id == related_partner:
            # See records from its related_partner (normally the parent)
            # but not other belonging to other users (like w/ child_of)
            partner_domains.append([(partner_field, operator, related_partner.id)])
            if main_account and main_account != related_partner:
                # See records from parent main account
                # NOTE: if main_account is the company,
                # they see records from the company as well.
                partner_domains.append([(partner_field, operator, main_account.id)])
        return expression.OR(partner_domains)

    def _make_address_domain(self):
        """Make domain for addresses related to current shopinvader partner.

        Admin users and main account users will see every address
        included the ones having a bound shopinvader user.

        Normal users will see their own addresses, plus:
        * The ones from their direct parent.
        * Publicly shared addresses from their siblings.

        If the policy is set to `main account` and the main account differs from
        the parent account they'll be able to see main account addresses too.
        """
        # Main users can always see everything down their hierarchy
        if self.is_admin_account or self.is_main_account:
            return [
                ("id", "child_of", self.record_id.id),
            ]
        # Change partner domain based on backend policy
        policy_field = self.backend_id.multi_user_records_policy
        related_partner = self[policy_field]
        main_account = self.main_partner_id

        def _make_parent_domain_leaf(partner):
            # public children records which are not users themselves
            return [
                ("id", "child_of", partner.id),
                ("shopinvader_bind_ids", "=", False),
                ("invader_address_share_policy", "=", "public"),
            ]

        specific_ids = [self.record_id.id]
        partner_domains = []

        # Always see own private or public addresses
        partner_domains.append(
            [
                ("parent_id", "=", self.record_id.id),
                ("shopinvader_bind_ids", "=", False),
            ]
        )

        if self.record_id != related_partner:
            if related_partner:
                # See public records from its related_partner (normally the parent)
                partner_domains.append(_make_parent_domain_leaf(related_partner))
                specific_ids.append(related_partner.id)

            if main_account and main_account != related_partner:
                # See public records from the main account
                partner_domains.append(_make_parent_domain_leaf(main_account))
                specific_ids.append(main_account.id)

        # Always include these IDS
        partner_domains.append([("id", "in", specific_ids)])
        return expression.OR(partner_domains)
