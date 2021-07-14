# Copyright 2019 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.tools.translate import _


class ShopinvaderNotification(models.Model):
    _inherit = "shopinvader.notification"

    def _get_all_notification(self):
        res = super()._get_all_notification()
        res.update(
            {
                "new_customer_welcome_not_validated": {
                    "name": _("New customer Welcome not validated"),
                    "model": "res.partner",
                },
                "customer_validated": {
                    "name": _("New customer validated"),
                    "model": "res.partner",
                },
                "address_created_not_validated": {
                    "name": _("Address created not validated"),
                    "model": "res.partner",
                },
                "address_validated": {
                    "name": _("Address validated"),
                    "model": "res.partner",
                },
            }
        )
        return res
