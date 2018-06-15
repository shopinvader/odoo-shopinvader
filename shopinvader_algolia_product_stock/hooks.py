# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def rename_module(cr):
    openupgrade.update_module_names(
        cr, [('shopinvader_algolia_stock',
              'shopinvader_algolia_product_stock')],
        merge_modules=True)
