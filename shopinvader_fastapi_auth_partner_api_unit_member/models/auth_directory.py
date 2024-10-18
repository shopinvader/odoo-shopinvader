# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AuthDirectory(models.Model):
    _inherit = "auth.directory"

    member_existing_template_id = fields.Many2one(
        "mail.template",
        "Mail Template Unit Member Already Existing",
        required=False,
        default=lambda self: self.env.ref(
            "shopinvader_fastapi_auth_partner_api_unit_member.email_already_existing",
            raise_if_not_found=False,
        ),
    )
