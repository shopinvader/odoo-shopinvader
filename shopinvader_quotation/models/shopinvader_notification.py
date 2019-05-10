# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models


class ShopinvaderNotification(models.Model):
    _inherit = "shopinvader.notification"

    def _get_all_notification(self):
        res = super()._get_all_notification()
        res.update(
            {
                "quotation_request": {
                    "name": _("Quotation request"),
                    "model": "sale.order",
                }
            }
        )
        return res
