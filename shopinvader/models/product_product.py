# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def _search_locomotive_backend_ids(self, operator, value):
        si_var_obj = self.env['shopinvader.variant']
        bindings = si_var_obj.search(
            [('backend_id.name', operator, value)])

        return [('id', 'in',
                 bindings.mapped('record_id').ids)]

    shopinvader_bind_ids = fields.One2many(
        'shopinvader.variant',
        'record_id',
        string='Shopinvader Binding')

    locomotive_backend_ids = fields.Many2many(
        string='ShopInvader Backends',
        comodel_name='locomotive.backend',
        compute='_compute_locomotive_backend_ids',
        store=False,
        search=_search_locomotive_backend_ids)
    active = fields.Boolean(inverse='_inverse_active')

    @api.multi
    def _inverse_active(self):
        self.filtered(lambda p: not p.active).mapped(
            'shopinvader_bind_ids').write({'active': False})

    @api.multi
    def _compute_locomotive_backend_ids(self):
        for rec in self:
            rec.locomotive_backend_ids = rec.mapped(
                'shopinvader_bind_ids.backend_id')
