# -*- coding: utf-8 -*-
#    Copyright (C) 2016 Akretion (http://www.akretion.com)
#    @author EBII MonsieurB <monsieurb@saaslys.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _get_sub_state_selection(self):
        res = super(SaleOrder, self)._get_sub_state_selection()

        res += [('wishlist',  'Wishlist')]
        return res
