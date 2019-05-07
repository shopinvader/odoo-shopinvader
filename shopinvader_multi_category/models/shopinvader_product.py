# -*- coding: utf-8 -*-
# Copyright 2017-2018 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ShopinvaderProduct(models.Model):
    _inherit = "shopinvader.product"

    def _get_categories(self):
        return (
            self.categ_ids + super(ShopinvaderProduct, self)._get_categories()
        )
