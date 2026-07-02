# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from ..schemas import AuthState

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    member_auth_state = fields.Selection(
        selection=[
            (AuthState.none.value, "None"),
            (AuthState.invited.value, "Invited"),
            (AuthState.accepted.value, "Accepted"),
        ],
        compute="_compute_member_auth_state",
        compute_sudo=True,
    )

    @api.depends("auth_partner_ids.password", "auth_partner_ids.encrypted_password")
    def _compute_member_auth_state(self):
        for record in self:
            auth = record.auth_partner_ids
            if not auth:
                record.member_auth_state = AuthState.none.value
                continue

            if len(auth) > 1:
                _logger.warning(
                    "Multiple auth_partner_ids for unit member partner %s, "
                    "using the first one",
                    record,
                )
                auth = auth[0]

            if auth.password or auth.encrypted_password:
                record.member_auth_state = AuthState.accepted.value
            else:
                record.member_auth_state = AuthState.invited.value

    @api.model
    def _invite_shopinvader_unit_member(self, member_id, directory):
        self._ensure_manager()
        member = self.browse(member_id)
        self._ensure_same_unit(member)
        if not member.email:
            raise UserError(_("Cannot invite a member without an email"))

        auth_with_email = self.env["auth.partner"].search(
            [
                ("login", "=", member.email),
                ("directory_id", "=", directory.id),
            ],
        )

        if auth_with_email:
            # If another member with the same email is already in the directory,
            if auth_with_email not in member.auth_partner_ids:
                directory._send_mail_background(
                    "member_existing",
                    auth_with_email,
                    member=member,
                    manager=self,
                )
                raise UserError(
                    # Do not leak the information that the email is already in use
                    _("Something went wrong, please contact the administrator"),
                )

            member_auth = auth_with_email
        else:
            member_auth = self.env["auth.partner"].create(
                {
                    "partner_id": member.id,
                    "login": member.email,
                    "directory_id": directory.id,
                }
            )

        member_auth._send_invite()
        return member
