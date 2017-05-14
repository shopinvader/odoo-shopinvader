# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class LocomotiveBackend(models.Model):
    _inherit = 'locomotive.backend'
    se_backend_id = fields.Many2one(
        'se.backend',
        'Search Engine Backend')

    def _clear_dead_se_content(self, model):
        # TODO remove dead content from Search Engine
        raise NotImplemented

    @api.multi
    def clear_dead_product(self):
        return self._clear_dead_se_content('shopinvader.product')

    @api.multi
    def clear_dead_category(self):
        return self._clear_dead_se_content('shopinvader.category')

    def _export_all_se_content(self, model):
        for record in self:
            for index in record.se_backend_id.index_ids:
                if index.model_id.model == model:
                    index.export_all()
        return True

    @api.multi
    def export_all_product(self):
        return self._export_all_se_content('shopinvader.variant')

    @api.multi
    def export_all_category(self):
        return self._export_all_se_content('shopinvader.category')
