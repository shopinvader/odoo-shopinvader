# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.connector_locomotivecms.connector import get_environment


class CommonCase(TransactionCase):

    def setUp(self, *args, **kwargs):
        super(CommonCase, self).setUp(*args, **kwargs)
        self.backend = self.env.ref('connector_locomotivecms.backend_1')
        self.shopinvader_session = {}
        # Compatibility with product_visible_discount
        if 'visible_discount' in self.env['product.pricelist']._fields:
            pricelist = self.env['product.pricelist'].search([])
            pricelist.write({'visible_discount': False})

    def _get_service(self, service_class, partner):
        model_name = service_class._model_name
        session = ConnectorSession.from_env(self.env)
        env = get_environment(session, model_name, self.backend.id)
        service = env.backend.get_class(service_class, session, model_name)
        return service(env, partner, self.shopinvader_session)


class ProductCommonCase(CommonCase):

    def setUp(self):
        super(ProductCommonCase, self).setUp()
        self.template = self.env.ref('product.product_product_4')
        self.variant = self.env.ref('product.product_product_4b')
        self.template.taxes_id = self.env.ref('shopinvader.tax_1')
        lang = self.env.ref('base.lang_en')
        self.env['shopinvader.product'].create({
            'record_id': self.template.id,
            'backend_id': self.backend.id,
            'lang_id': lang.id
            })
        self.shopinvader_variants = self.env['shopinvader.variant'].search([
            ('record_id', 'in', self.template.product_variant_ids.ids),
            ('backend_id', '=', self.backend.id)])
        self.shopinvader_variant = self.env['shopinvader.variant'].search([
            ('record_id', '=', self.variant.id),
            ('backend_id', '=', self.backend.id)])
