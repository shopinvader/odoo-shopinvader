# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openerp import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    locomotive_backend_id = fields.Many2one(
        'locomotive.backend',
        'Backend')
    cart_state = fields.Char()
    anonymous_email = fields.Char()


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_url = fields.Char(compute='_compute_product_url')

    def _get_product_url(self, backend, size='medium'):
        for image in self.product_id.image_ids:
            for binding in image.locomotive_bind_ids:
                if binding.backend_id == backend and binding.size == size:
                    return binding.url

    def _compute_product_url(self):
        for record in self:
            loco_backend = record.order_id.locomotive_backend_id
            if loco_backend:
                record.product_url = record._get_product_url(loco_backend)
