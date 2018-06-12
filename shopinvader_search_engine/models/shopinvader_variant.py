# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ShopinvaderVariant(models.Model):
    _inherit = ['shopinvader.variant', 'se.binding']
    _name = 'shopinvader.variant'
    _description = 'Shopinvader Variant'

    index_id = fields.Many2one(
        compute="_compute_index",
        store=True,
        required=False)

    @api.depends('backend_id.se_backend_id')
    def _compute_index(self):
        for record in self:
            se_backend = record.backend_id.se_backend_id
            if se_backend:
                record.index_id = self.env['se.index'].search([
                    ('backend_id', '=', se_backend.id),
                    ('model_id.model', '=', record._name),
                    ('lang_id', '=', record.lang_id.id)
                    ])
