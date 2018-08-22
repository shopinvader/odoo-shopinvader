# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ShopinvaderBackend(models.Model):
    _inherit = 'shopinvader.backend'

    se_backend_id = fields.Many2one(
        'se.backend',
        'Search Engine Backend')

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
