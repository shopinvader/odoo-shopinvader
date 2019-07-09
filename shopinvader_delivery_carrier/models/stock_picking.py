# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.multi
    def _notify_backend(self, notification):
        """
        Send the notification to current recordset
        :param notification: str
        :return: bool
        """
        if notification == "stock_picking_outgoing_validated":
            self._notify_backend_outgoing(notification)
        return True

    @api.multi
    def _notify_backend_outgoing(self, notification):
        """
        Notify current picking with outgoing type
        :param notification: str
        :return: bool
        """
        picking_outgoing = self.filtered(
            lambda p: p.picking_type_id.code == "outgoing"
        )
        all_move_lines = picking_outgoing.mapped("move_lines")
        backends = picking_outgoing._get_related_backends()

        def filter_line(l, b):
            lbackend = l.sale_line_id.order_id.shopinvader_backend_id
            return lbackend == b

        for backend in backends:
            move_lines = all_move_lines.filtered(
                lambda l, b=backend: filter_line(l, b)
            )
            pickings = move_lines.mapped("picking_id")
            for picking in pickings:
                backend._send_notification(notification, picking)
        return True

    @api.multi
    def _get_related_backends(self):
        """
        Get backend related to current pickings
        :return: shopinvader.backend recordset
        """
        move_lines = self.mapped("move_lines")
        # Load backend from related sale order lines
        backends = move_lines.mapped(
            "sale_line_id.order_id.shopinvader_backend_id"
        )
        return backends

    @api.multi
    def action_done(self):
        """
        Inherit to update the invoice state if necessary
        :return:
        """
        result = super(StockPicking, self).action_done()
        self._notify_backend("stock_picking_outgoing_validated")
        return result
