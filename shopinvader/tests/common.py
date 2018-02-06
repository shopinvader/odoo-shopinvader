# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.tests.common import SavepointComponentCase
from contextlib import contextmanager
from odoo.addons.component.core import WorkContext
from odoo.addons.base_rest.controllers.main import _PseudoCollection


class CommonCase(SavepointComponentCase):

    def setUp(self, *args, **kwargs):
        super(CommonCase, self).setUp(*args, **kwargs)
        self.backend = self.env.ref('shopinvader.backend_1')
        self.backend.bind_all_product()
        self.shopinvader_session = {}
        # Compatibility with product_visible_discount
        if 'visible_discount' in self.env['product.pricelist']._fields:
            pricelist = self.env['product.pricelist'].search([])
            pricelist.write({'visible_discount': False})

    @contextmanager
    def work_on_services(self, **params):
        params = params or {}
        if 'locomotive_backend' not in params:
            params['locomotive_backend'] = self.backend
        if 'shopinvader_session' not in params:
            params['shopinvader_session'] = {}
        collection = _PseudoCollection('locomotive.backend',  self.env)
        yield WorkContext(model_name='rest.service.registration',
                          collection=collection, **params)


class ProductCommonCase(CommonCase):

    def setUp(self):
        super(ProductCommonCase, self).setUp()
        self.template = self.env.ref(
            'product.product_product_4_product_template')
        self.variant = self.env.ref('product.product_product_4b')
        self.template.taxes_id = self.env.ref('shopinvader.tax_1')
        self.shopinvader_variants = self.env['shopinvader.variant'].search([
            ('record_id', 'in', self.template.product_variant_ids.ids),
            ('backend_id', '=', self.backend.id)])
        self.shopinvader_variant = self.env['shopinvader.variant'].search([
            ('record_id', '=', self.variant.id),
            ('backend_id', '=', self.backend.id)])
