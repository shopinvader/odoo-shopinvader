# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class NosqlProductProduct(models.Model):
    _inherit = 'nosql.product.product'

    def _get_categories(self):
        categs = super(NosqlProductProduct, self)._get_categories()
        categs += record.categ_ids
        return categs
