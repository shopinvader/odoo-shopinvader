# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com)
# Copyright 2018 ACSONE SA/NV
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class ShopinvaderVariant(models.Model):
    _inherit = 'shopinvader.variant'

    # We should have a special field to save what is actually exported.
    # But we don't have yet this information.
    # We could maybe use the write_date of the odoo record (product.product in
    # this case) but this write_date is not updated for computed fields.
    # We can save all exported values into a special field but in which format?
    # It's depend on the index, backend and the mapper (json,...) used.
    # So for this usage only, we save the stock value into this field and we
    # compare it to know if the update is useful or not.
    last_stock_value = fields.Float(
        help="Last stock value sent",
        readonly=True,
    )

    @api.multi
    def _get_se_backend_stock_value(self):
        """
        Get the stock value using the stock field defined on the se backend.
        If a stock field is not defined on the backend, return 0
        :return: float
        """
        self.ensure_one()
        field = self.backend_id.se_backend_id.product_stock_field_id
        stock_value = 0
        if field:
            stock_value = self[field.name]
        return stock_value

    @api.multi
    def _update_stock_qty_sent(self, value):
        """
        Update the last quantity sent to related backend with the given value
        :param value: float
        :return: bool
        """
        return self.write({
            'last_stock_value': value,
        })
