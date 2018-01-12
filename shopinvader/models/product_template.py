# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _search_locomotive_backend_ids(self, operator, value):
        si_var_obj = self.env['shopinvader.product']
        bindings = si_var_obj.search(
            [('backend_id.name', operator, value)])

        return [('id', 'in',
                 bindings.mapped('record_id').ids)]

    shopinvader_bind_ids = fields.One2many(
        'shopinvader.product',
        'record_id',
        string='Shopinvader Binding')

    locomotive_backend_ids = fields.Many2many(
        string='ShopInvader Backends',
        comodel_name='locomotive.backend',
        compute='_compute_locomotive_backend_ids',
        store=False,
        search=_search_locomotive_backend_ids)

    description = fields.Html(translate=True)
    active = fields.Boolean(inverse='_inverse_active')

    @api.multi
    def _inverse_active(self):
        inactive = self.filtered(lambda p: not p.active)
        inactive.mapped('shopinvader_bind_ids').write(
            {'active': False})

    def _compute_locomotive_backend_ids(self):
        for rec in self:
            rec.locomotive_backend_ids = rec.mapped(
                'shopinvader_bind_ids.backend_id')

    @api.multi
    def unlink(self):
        for record in self:
            # TODO we should propose to redirect the old url
            record.shopinvader_bind_ids.unlink()
        return super(ProductTemplate, self).unlink()
