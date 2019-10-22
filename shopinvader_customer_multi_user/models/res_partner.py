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

    invader_user_token = fields.Char(readonly=True, index=True)
    # `type` is the base field from odoo core :/
    type = fields.Selection(
        selection_add=[("invader_client_user", "Invader client user")]
    )

    _sql_constraints = [
        (
            "unique_invader_user_token",
            "unique(invader_user_token)",
            "Already exists in database",
        )
    ]

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

    @api.multi
    def assign_invader_user_token(self, token=None):
        token = token or self._generate_invader_user_token()
        self.write({"invader_user_token": token})

    @api.multi
    def action_regenerate_invader_user_token(self):
        # NOTE: for buttons we cannot use `_generate_invader_user_token`
        # directly because the client passes the context as 1st argument
        # hence the token turns to be the ctx dict as a string :/
        self.assign_invader_user_token()

    def invader_client_user_type(self):
        return "invader_client_user"

    @api.multi
    def is_invader_user(self):
        self.ensure_one()
        return self.type == self.invader_client_user_type()

    # @api.multi
    # def get_parent_binding(self, backend):
    #     self.ensure_one()
    #     parent_partner = self.parent_id
    #     if not parent_partner:
    #         return self.browse()
    #     return self.env["shopinvader.partner"].search(
    #         [
    #             ("record_id", "=", parent_partner.id),
    #             ("backend_id", "=", backend.id),
    #         ],
    #         limit=1,
    #     )
