# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    shopinvader_backend_id = fields.Many2one(
        "shopinvader.backend", "Shopinvader Backend"
    )

    @api.multi
    def invoice_validate(self):
        res = super(AccountInvoice, self).invoice_validate()
        for record in self:
            backend = record.shopinvader_backend_id
            if backend:
                backend._send_notification("invoice_open", record)
        return res
