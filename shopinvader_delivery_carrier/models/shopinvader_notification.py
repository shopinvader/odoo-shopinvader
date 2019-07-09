# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _, api, models


class ShopinvaderNotification(models.Model):
    _inherit = "shopinvader.notification"

    @api.model
    def _get_picking_notification(self):
        """
        Get every delivery notifications
        :return: dict
        """
        return {
            "stock_picking_outgoing_validated": {
                "name": _("Delivery order validated"),
                "model": "stock.picking",
            }
        }

    def _get_all_notification(self):
        """
        Inherit to add gift list notifications
        :return: dict
        """
        result = super(ShopinvaderNotification, self)._get_all_notification()
        picking_notification = self._get_picking_notification()
        if picking_notification:
            result.update(picking_notification)
        return result
