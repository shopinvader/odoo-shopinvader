# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class ShopinvaderStoreConfig(models.TransientModel):
    _name = 'shopinvader.store.config'
    _description = 'Shopinvader Store Config'

    data = fields.Binary('Store Config', readonly=True)
    filename = fields.Char('Filename')
