# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = "product.category"
    # TODO MIGRATE Should be done in a separated module
    # _inherit = [_name, "storage.image.owner"]

    shopinvader_bind_ids = fields.One2many(
        'shopinvader.category',
        'record_id',
        string='Shopinvader Binding')
    filter_ids = fields.Many2many(
        comodel_name='product.filter',
        string='Filter')
