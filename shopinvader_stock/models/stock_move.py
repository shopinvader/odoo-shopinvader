# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com)
# Copyright 2018 ACSONE SA/NV
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def _jobify_product_stock_update(self):
        """
        Trigger on update on related backend if the product quantity has been
        updated since last sync.
        :return: bool
        """
        codes = ['incoming', 'outgoing']
        moves = self.filtered(lambda m: m.picking_type_id.code in codes)
        moves = moves.with_prefetch(self._prefetch)
        if moves:
            description = "Update shopinvader variants (stock update trigger)"
            moves.with_delay(
                description=description)._product_stock_update_all()
        return True

    @api.multi
    def action_cancel(self):
        """

        :return: bool
        """
        result = super(StockMove, self).action_cancel()
        self._jobify_product_stock_update()
        return result

    @api.multi
    def action_confirm(self):
        """

        :return: stock.move recordset
        """
        result = super(StockMove, self).action_confirm()
        self._jobify_product_stock_update()
        return result

    @api.multi
    def action_done(self):
        """

        :return: bool
        """
        result = super(StockMove, self).action_done()
        self._jobify_product_stock_update()
        return result
