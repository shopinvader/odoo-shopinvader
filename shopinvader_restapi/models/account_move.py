# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    shopinvader_backend_id = fields.Many2one(
        "shopinvader.backend", "Shopinvader Backend"
    )

    def _post(self, soft=True):
        res = super(AccountMove, self)._post(soft=soft)
        for record in self:
            backend = record.shopinvader_backend_id
            if record.move_type == "out_invoice" and backend:
                backend._send_notification("invoice_open", record)
        return res
