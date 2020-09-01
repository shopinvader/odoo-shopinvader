# Copyright 2019 Camptocamp SA (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import random
import string

from odoo import api, fields, models


def _generate_token(length=10):
    return "".join(
        random.choice(string.ascii_letters + string.digits)
        for __ in range(length)
    )


class ResPartner(models.Model):

    _inherit = "res.partner"

    invader_user_token = fields.Char(
        readonly=True,
        index=True,
        help="The token is automatically generated "
        "when a binding to the shop is created.",
    )
    is_invader_user = fields.Boolean(
        compute="_compute_is_invader_user",
        help="At least one backend has an invader user for this partner.",
    )

    _sql_constraints = [
        (
            "unique_invader_user_token",
            "unique(invader_user_token)",
            "Already exists in database",
        )
    ]

    @api.depends("shopinvader_bind_ids")
    def _compute_is_invader_user(self):
        for rec in self:
            rec.is_invader_user = any(
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
        token = token or self._generate_invader_user_token()
        self.write({"invader_user_token": token})

    def action_regenerate_invader_user_token(self):
        # NOTE: for buttons we cannot use `_generate_invader_user_token`
        # directly because the client passes the context as 1st argument
        # hence the token turns to be the ctx dict as a string :/
        self.assign_invader_user_token()
