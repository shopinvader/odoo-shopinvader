# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    shopinvader_write_date = fields.Datetime(
        help="Specific write_date used for shopinvader."
    )

    def _fill_shopinvader_write_date(self, values):
        """
        During write, always update the shopinvader_write_date.
        If the key skip_shopinvader_write_date in context is set to False OR if
        values is empty, the field is not updated.
        :param values: dict
        :return: dict
        """
        if values and not self.env.context.get(
            "skip_shopinvader_write_date", False
        ):
            values.update({"shopinvader_write_date": fields.Datetime.now()})
        return values

    @api.multi
    def write(self, vals):
        """
        Inherit to manage the shopinvader_write_date
        :param vals: dict
        :return: bool
        """
        vals = self._fill_shopinvader_write_date(vals)
        return super(SaleOrder, self).write(vals)
