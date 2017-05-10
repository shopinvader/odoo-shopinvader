# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class ShopinvaderVariant(models.Model):
    _inherit = 'shopinvader.variant'

    cross_sellings = fields.Many2many(
        comodel_name='product.template',
        compute='_compute_link')
    relateds = fields.Many2many(
        comodel_name='product.template',
        compute='_compute_link')
    up_sellings = fields.Many2many(
        comodel_name='product.template',
        compute='_compute_link')

    def _get_related_product(self, link_type):
        self.ensure_one()
        res = []
        for link in self.product_link_ids:
            if link.type == link_type and link.is_active:
                for binding in\
                        link.linked_product_tmpl_id.shopinvader_bind_ids:
                    if binding.backend_id == self.backend_id:
                        res.append(link.linked_product_tmpl_id.id)
        return res

    def _compute_link(self):
        for record in self:
            record.cross_sellings = record._get_related_product('cross_sell')
            record.relateds = record._get_related_product('related')
            record.up_sellings = record._get_related_product('up_sell')
