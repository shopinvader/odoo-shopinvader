# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PaymentProvider(models.Model):

    _inherit = "payment.provider"

    shopinvader_auto_confirm_linked_so = fields.Boolean(
        string="Auto-confirm quotations",
        help="If ticked, the linked quotation will be automatically confirmed "
        "into a sale order. If not ticked, the quotation will only be "
        "sent to the customer.",
    )
