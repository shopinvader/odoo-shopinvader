# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ShopinvaderVariantBindingWizard(models.TransientModel):

    _name = 'shopinvader.variant.binding.wizard'
    _description = "Wizard to bind products to a shopinvader catalogue"

    backend_id = fields.Many2one(
        string='ShopInvader Backend',
        comodel_name='locomotive.backend',
        required=True,
        ondelete='cascade')
    product_ids = fields.Many2many(
        string='Products',
        comodel_name='product.product',
        ondelete='cascade')

    @api.model
    def default_get(self, fields_list):
        res = super(ShopinvaderVariantBindingWizard, self).default_get(
            fields_list)
        backend_id = self.env.context.get('active_id', False)
        if backend_id:
            res['backend_id'] = backend_id
        return res

    @api.multi
    def _get_binded_templates(self):
        """
        return a dict of binded shopinvader.product by product template id
        :return:
        """
        self.ensure_one()
        binding = self.env['shopinvader.product']
        product_template_ids = self.mapped('product_ids.product_tmpl_id')
        binded_templates = binding.with_context(active_test=False).search(
            [('record_id', 'in', product_template_ids.ids),
             ('backend_id', '=', self.backend_id.id)])
        ret = {bt.record_id: bt for bt in binded_templates}
        for product in self.mapped('product_ids.product_tmpl_id'):
            product_tmpl_id = product
            bind_record = ret.get(product_tmpl_id)
            if not bind_record:
                data = {
                    'record_id': product.id,
                    'backend_id': self.backend_id.id}
                ret[product_tmpl_id] = binding.create(data)
            elif not bind_record.active:
                bind_record.write({'active': True})
        return ret

    @api.multi
    def bind_products(self):
        for wizard in self:
            binded_templates = self._get_binded_templates()
            binding = self.env['shopinvader.variant']
            for product in self.product_ids:
                data = {
                    'record_id': product.id,
                    'backend_id': wizard.backend_id.id,
                    'shopinvader_product_id':
                        binded_templates[product.product_tmpl_id].id
                }
                bind_record = binding.with_context(active_test=False).search(
                    [('record_id', '=', product.id),
                     ('backend_id', '=', wizard.backend_id.id)])
                if not bind_record:
                    binding.create(data)
                elif not bind_record.active:
                    bind_record.write({'active': True})
