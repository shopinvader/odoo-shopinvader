# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import api, fields, models


class ShopinvaderBackend(models.Model):

    _inherit = "shopinvader.backend"

    password_validity = fields.Integer(
        default=0,
        string="Password Validity (days)",
        help="Define here the user password validity (in days) on Website. "
        "If the validity is passed, an email would be sent to reset it."
        "To deactivate it, set it to 0.",
    )
    password_reset_template_id = fields.Many2one(
        comodel_name="mail.template",
        domain=[("model_id", "=", "shopinvader.partner")],
        string="Password Reset Template",
    )
    password_reset_token_default_validity = fields.Selection(
        selection=lambda self: self._get_selection_token_validity(),
        default=lambda self: self._get_default_token_validity(),
    )

    @api.model
    def _get_selection_token_validity(self):
        return [
            ("manually", "Manually"),
            ("6-hours", "6 Hours"),
            ("2-days", "2-days"),
            ("7-days", "7 Days"),
            ("14-days", "14 Days"),
        ]

    @api.model
    def _get_default_token_validity(self):
        return "6-hours"

    def reset_expired_password(self):
        self.ensure_one()
        partners = self.env["shopinvader.partner"].search(
            self._get_expired_password_domain()
        )
        template = self.password_reset_template_id
        wizard = self.env["shopinvader.reset.password"].create(
            {
                "partner_ids": [(6, 0, partners.ids)],
                "template_id": template.id,
                "delay": self.password_reset_token_default_validity,
            }
        )
        wizard.confirm()

    @api.model
    def _launch_reset_expired_password(self):
        for backend in self.env["shopinvader.backend"].search(
            [("password_validity", ">", 0)]
        ):
            backend.with_delay().reset_expired_password()

    def _get_expired_password_domain(self):
        self.ensure_one()
        pivot_date = fields.Datetime.from_string(fields.Datetime.now()) + timedelta(
            days=self.password_validity
        )
        pivot_date_string = fields.Datetime.to_string(pivot_date)
        domain = [
            ("backend_id", "=", self.id),
            ("last_pwd_reset_datetime", "<", pivot_date_string),
        ]
        return domain
