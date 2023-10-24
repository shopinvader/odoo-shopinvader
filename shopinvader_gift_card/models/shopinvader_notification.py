# Copyright (C) 2022 Akretion (<http://www.akretion.com>).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.tools.translate import _


class ShopinvaderNotification(models.Model):
    _inherit = "shopinvader.notification"

    def _get_all_notification(self):
        res = super()._get_all_notification()
        res.update(
            {
                "gift_card_created": {
                    "name": _("Email Gift card created to the Buyer"),
                    "model": "gift.card",
                },
                "gift_card_activated": {
                    "name": _("Email gift Card to the Beneficiary"),
                    "model": "gift.card",
                },
            }
        )
        return res
