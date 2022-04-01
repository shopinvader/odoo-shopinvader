# Copyright (C) 2022 Akretion (<http://www.akretion.com>).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_post(self):
        for move in self:
            lines = [
                line
                for line in move.invoice_line_ids.mapped("sale_line_ids")
                .mapped("order_id")
                .order_line
                if line.gift_card_id
            ]
            for line in lines:
                gift_card = line.gift_card_id
                # Check the start date of the gift card and update its state
                self._update_gift_card_state(gift_card)
                # Confirm sale of the gift card by mail to the buyer
                gift_card.send_email_to_buyer()
        return super().action_post()

    def _update_gift_card_state(self, gift_card):
        if gift_card.state == "draft":
            gift_card.state = "not_activated"
        gift_card._compute_state()
        if gift_card.state == "active" and not gift_card.email_confirmation_send:
            gift_card.send_email_to_beneficiary()

    def _create_gift_card(self):
        # Cancel the initial method to create a gift card, avoiding duplicates.
        for line in (
            self.invoice_line_ids.mapped("sale_line_ids").mapped("order_id").order_line
        ):
            if line.gift_card_id:
                self = self.with_context(gift_card_created=True)
        return super()._create_gift_card()
