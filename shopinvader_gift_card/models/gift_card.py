# Copyright (C) 2022 Akretion (<http://www.akretion.com>).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class GiftCard(models.Model):
    _inherit = "gift.card"

    comment = fields.Text(string="Comment")
    beneficiary_name = fields.Char(string="Beneficiary Name")
    beneficiary_email = fields.Char(string="Beneficiary Email")
    buyer_name = fields.Char(string="Buyer Name")
    buyer_email = fields.Char(string="Buyer Email")
    email_confirmation_send = fields.Boolean(default=False)
    shopinvader_backend_id = fields.Many2one(
        "shopinvader.backend", "Shopinvader Backend"
    )

    state = fields.Selection(
        selection_add=[("draft", "Draft")],
        ondelete={"draft": "set default"},
    )

    user_id = fields.Many2one(related="sale_id.user_id")

    def cron_email_to_gift_card_beneficiary(self):
        card_mails_list_to_send = self.search(
            [
                ("beneficiary_email", "!=", False),
                ("email_confirmation_send", "=", False),
                ("start_date", "<=", fields.Date.today()),
            ]
        )
        for card in card_mails_list_to_send:
            card.state = "active"
            card.send_email_to_beneficiary()

    def send_email_to_beneficiary(self):
        if self.shopinvader_backend_id:
            self.shopinvader_backend_id._send_notification("gift_card_activated", self)
            self.email_confirmation_send = True

    def send_email_to_buyer(self):
        if self.shopinvader_backend_id:
            self.shopinvader_backend_id._send_notification("gift_card_created", self)

    @api.model
    def create(self, vals):
        if self._context.get("gift_card_created", False):
            return
        else:
            return super().create(vals)


class GiftCardLine(models.Model):
    _inherit = "gift.card.line"

    sale_order_id = fields.Many2one(comodel_name="sale.order", readonly=True)
