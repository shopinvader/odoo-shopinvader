# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ShopinvaderBackend(models.Model):
    _inherit = 'shopinvader.backend'

    @api.model
    def _get_model_domain(self):
        res = self.env['se.index']._get_model_domain()
        return res

    se_backend_id = fields.Many2one(
        'se.backend',
        'Search Engine Backend')

    model_ids = fields.One2many(
        'ir.model',
        string='Model',
        domain=_get_model_domain)
    
    index_ids = fields.One2many(
        'se.index',
        related='se_backend_id.index_ids',
    )

    @api.multi
    def force_recompute_all_binding_index(self):
        self.mapped('se_backend_id.index_ids').force_recompute_all_binding()
        return True

    @api.multi
    def force_batch_export_index(self):
        for index in self.mapped('se_backend_id.index_ids'):
            index.force_batch_export()
        return True

    @api.multi
    def clear_index(self):
        for index in self.mapped('se_backend_id.index_ids'):
            index.clear_index()
        return True

    @api.multi
    def add_misssing_index(self):
        for index in self.mapped('se_backend_id.index_ids'):
            index.clear_index()
        return True