# -*- coding: utf-8 -*-
# Copyright 2017-2018 Akretion (http://www.akretion.com).
# Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    typology = fields.Selection(selection_add=[('quotation', 'Quotation')])
    shopinvader_state = fields.Selection(selection_add=[
        ('estimating', 'Estimating Quotation'),
        ('estimated', 'Estimated Quotation')])

    def _get_shopinvader_state(self):
        self.ensure_one()
        if self.typology == 'quotation' and self.state == 'draft':
            return 'estimating'
        if self.typology == 'quotation' and self.state == 'draft':
            return 'estimated'
        return super(SaleOrder, self)._get_shopinvader_state()
