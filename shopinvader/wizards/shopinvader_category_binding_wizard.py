# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class ShopinvaderCategoryBindingWizard(models.TransientModel):
    """
    Wizard used to bind product.category to shopinvader.category
    """
    _name = 'shopinvader.category.binding.wizard'
    _description = "Wizard to bind categories to a shopinvader categories"

    backend_id = fields.Many2one(
        'locomotive.backend',
        'ShopInvader Backend',
        required=True,
        ondelete='cascade',
    )
    product_category_ids = fields.Many2many(
        'product.category',
        string='Categories',
        ondelete='cascade',
    )

    @api.model
    def default_get(self, fields_list):
        result = super(ShopinvaderCategoryBindingWizard, self).default_get(
            fields_list)
        backend_id = self.env.context.get('active_id')
        if backend_id:
            result.update({
                'backend_id': backend_id,
            })
        return result

    @api.multi
    def action_bind_categories(self):
        shopinv_categ_obj = self.env['shopinvader.category']
        for wizard in self:
            for lang in wizard.backend_id.lang_ids:
                for category in wizard.product_category_ids:
                    binded_categories = category.shopinvader_bind_ids
                    bind_record = binded_categories.filtered(
                        lambda p: p.record_id.id == category.id)
                    bind_record = bind_record.with_prefetch(self._prefetch)
                    if not bind_record:
                        data = {
                            'record_id': category.id,
                            'backend_id': wizard.backend_id.id,
                            'lang_id': lang.id,
                        }
                        shopinv_categ_obj.create(data)
                    elif not bind_record.active:
                        bind_record.write({'active': True})
