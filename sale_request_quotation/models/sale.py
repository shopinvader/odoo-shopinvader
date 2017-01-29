# -*- coding: utf-8 -*-
#    Copyright (C) 2016 Akretion (http://www.akretion.com)
#    @author EBII MonsieurB <monsieurb@saaslys.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    sub_state = fields.Selection(
        selection_add=[('request_quotation',  'Request Quotation')])
