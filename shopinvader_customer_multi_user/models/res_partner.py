# Copyright 2019 Camptocamp SA (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import random
import string

from odoo import api, fields, models


def _generate_token(length=10):
    return "".join(
        random.choice(string.ascii_letters + string.digits) for __ in range(length)
    )


class ResPartner(models.Model):

    _inherit = "res.partner"

    invader_user_token = fields.Char(
        readonly=True,
        index=True,
        help="The token is automatically generated "
        "when a binding to the shop is created.",
    )
    has_invader_user = fields.Boolean(
        string="Has an invader user",
        compute="_compute_has_invader_user",
        help="At least one backend has an invader user for this partner.",
    )
    invader_address_share_policy = fields.Selection(
        [
            ("public", "Public"),
            ("private", "Private"),
        ],
        string="Shop Address Share Policy",
        help="In a multi user environment, controls who can view this address\n\n"
        "* `Public`: Shared among all company's users.\n"
        "* `Private`: Only the user who created it and company's admin users.\n",
        default="public",
    )

    _sql_constraints = [
        (
            "unique_invader_user_token",
            "unique(invader_user_token)",
            "Already exists in database",
        )
    ]

    @api.depends("shopinvader_bind_ids.is_invader_user")
    def _compute_has_invader_user(self):
        for rec in self:
            rec.has_invader_user = any(
                rec.mapped("shopinvader_bind_ids.is_invader_user")
            )

    @api.model
    def _generate_invader_user_token(self, length=10):
        """Generate a random token."""
        _token = _generate_token(length=length)
        while self.find_by_invader_user_token(_token):
            _token = _generate_token()
        return _token

    @api.model
    def find_by_invader_user_token(self, token):
        return self.search([("invader_user_token", "=", token)], limit=1)

    def assign_invader_user_token(self, token=None):
        for rec in self:
            token = token or self._generate_invader_user_token()
            rec.invader_user_token = token

    def action_regenerate_invader_user_token(self):
        # NOTE: for buttons we cannot use `_generate_invader_user_token`
        # directly because the client passes the context as 1st argument
        # hence the token turns to be the ctx dict as a string :/
        self.assign_invader_user_token()

    def get_shop_partner(self, backend):
        default = super().get_shop_partner(backend)
        if not backend.customer_multi_user:
            return default
        invader_partner = self._get_invader_partner(backend)
        # If this is just a simple user,
        # by default the main account is the parent company
        if invader_partner.is_invader_user:
            mapped_field = backend.multi_user_profile_policy
            if invader_partner.mapped(mapped_field):
                return invader_partner.mapped(mapped_field)
            return invader_partner.record_id
        return default
