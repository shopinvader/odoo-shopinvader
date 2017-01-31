# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    use_different_invoice_address = fields.Boolean(default=True)

    def _set_invoice_address(self):
        self.ensure_one()
        if not self.use_different_invoice_address\
                and self.partner_invoice_id != self.partner_shipping_id:
            self.partner_invoice_id = self.partner_shipping_id

    @api.multi
    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        for record in self:
            record._set_invoice_address()
        return res

    @api.model
    def create(self, vals):
        record = super(SaleOrder, self).create(vals)
        record._set_invoice_address()
        return record
