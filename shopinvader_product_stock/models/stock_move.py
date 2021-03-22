# Copyright 2018 Akretion (http://www.akretion.com)
# Copyright 2018 ACSONE SA/NV
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, models

from odoo.addons.queue_job.job import identity_exact


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_product_to_update(self):
        # Maybe we can be more restrictive
        # depending of the move location and destination
        # For now we take all moves and bound products
        return self.mapped("product_id").filtered(
            lambda p: p.is_shopinvader_binded
        )

    def _jobify_product_stock_update(self):
        """
        Trigger on update on related backend if the product quantity has been
        updated since last sync.
        :return: bool
        """
        products = self._get_product_to_update()
        if products:
            description = _(
                "Update shopinvader variants (stock update trigger)"
            )
            products.with_delay(
                description=description, identity_key=identity_exact
            ).synchronize_all_binding_stock_level()
        return True

    def _action_cancel(self):
        """

        :return: bool
        """
        result = super()._action_cancel()
        self._jobify_product_stock_update()
        return result

    def _action_confirm(self, merge=True, merge_into=False):
        """

        :return: stock.move recordset
        """
        # action_confirm on stock_move method can return a new recorset in
        # case of BOM
        result = super()._action_confirm(merge=merge, merge_into=merge_into)
        result._jobify_product_stock_update()
        return result

    def _action_done(self, cancel_backorder=False):
        """

        :return: bool
        """
        result = super()._action_done(cancel_backorder=cancel_backorder)
        result._jobify_product_stock_update()
        return result
