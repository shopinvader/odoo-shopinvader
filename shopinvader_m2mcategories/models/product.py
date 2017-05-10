# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models


class ShopinvaderVariant(models.Model):
    _inherit = 'shopinvader.variant'

    def _get_categories(self):
        categs = super(ShopinvaderVariant, self)._get_categories()
        categs += self.categ_ids
        return categs
