# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.tests.common import SavepointComponentCase
from contextlib import contextmanager
from odoo.addons.component.core import WorkContext
from odoo.addons.base_rest.controllers.main import _PseudoCollection
from odoo.addons.base_rest.tests.common import BaseRestCase
from odoo.addons.queue_job.job import Job


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

    def _init_job_counter(self):
        self.existing_job = self.env['queue.job'].search([])

    @property
    def created_jobs(self):
        return self.env['queue.job'].search([]) - self.existing_job

    def _check_nbr_job_created(self, nbr):
        self.assertEqual(len(self.created_jobs), nbr)

    def _perform_created_job(self):
        for job in self.created_jobs:
            Job.load(self.env, job.uuid).perform()


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


class ShopinvaderRestCase(BaseRestCase):

    def setUp(self, *args, **kwargs):
        super(ShopinvaderRestCase, self).setUp(*args, **kwargs)
        self.backend = self.env.ref('shopinvader.backend_1')
        self.api_key = self.backend.auth_api_key_id\
            ._get_keychain_account()._get_password()
