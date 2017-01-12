# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# @author Delli Chafique  <delli.chafique@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    sub_state = fields.Selection(
        selection=[],
        help=("Gives additionnal status to sales order for example for "
              "the production or the shipment."))
