# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    media_ids = fields.Many2many(
        comodel_name='ir.attachment.media',
        string='Media')
