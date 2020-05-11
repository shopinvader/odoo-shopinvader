# Copyright 2018-2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ShopinvaderBackend(models.Model):

    _inherit = "shopinvader.backend"

    is_guest_mode_allowed = fields.Boolean(
        "Allows guest mode",
        help="When true, the customer can place an order without having to "
        "create a customer account.",
    )

    guest_account_expiry_delay = fields.Integer(
        help="Number of days a guest account remains active. If at the end of"
        "the delay (create date + delay), the guest_mode flag is still "
        "True on the shopinvader partner, the record becomes inactive",
        default=7,
    )

    @api.constrains("is_guest_mode_allowed")
    def _check_is_guest_mode_allowed(self):
        for record in self:
            if record.is_guest_mode_allowed:
                return
            #  We can't disable guest mode if guest account exists!
            guest_partners = self.env["shopinvader.partner"].search(
                [("backend_id", "=", record.id), ("is_guest", "=", True)]
            )
            if guest_partners:
                raise ValidationError(
                    _(
                        "You can't remove guest mode since guest partners "
                        "already exists."
                    )
                )

    @api.constrains("guest_account_expiry_delay", "is_guest_mode_allowed")
    def _check_guest_account_expiry_delay(self):
        for record in self:
            if not record.is_guest_mode_allowed:
                continue
            if record.guest_account_expiry_delay <= 0:
                raise ValidationError(
                    _(
                        "You must specify a positive value for the expiry "
                        "delay if guest mode is allowed"
                    )
                )
