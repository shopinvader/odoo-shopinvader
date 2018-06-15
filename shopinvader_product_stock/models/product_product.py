# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com)
# Copyright 2018 ACSONE SA/NV
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.fields import first
from odoo.addons.queue_job.job import job
from odoo.tools import float_compare
from odoo import api, exceptions, models, _


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def _job_stock_can_start(self):
        """
        Check if the queue job can start (or should wait something)
        :return: bool
        """
        return True

    @api.model
    def _get_stock_mapper(self):
        """
        Get the mapper to use.
        Return None to have the default mapper
        :return: str
        """
        return None

    @api.multi
    @job(default_channel='root.search_engine')
    def _product_stock_update_all(self):
        """
        The goal of this function is to have shopinvader.variant grouped by
        index.
        This result will be given to another job (1 job/index). So in case
        of failure, only the export of 1 index should be re-launched.
        :return:
        """
        if not self._job_stock_can_start():
            message = _("Another related queue job is running...")
            raise exceptions.MissingError(message)
        products = self
        shopinvader_variants = self._get_shopinvader_variants_from_product(
            products)
        mapper = self._get_stock_mapper()
        all_backend = shopinvader_variants.mapped(
            "se_backend_id")
        all_index = all_backend.mapped("index_ids")
        for index in all_index:
            # Get shopinvader.variant of this index
            variants_index = shopinvader_variants.filtered(
                lambda s, i=index: s.index_id.id == i.id)
            variants_index = variants_index.with_prefetch(self._prefetch)
            description = "Update shopinvader variants (stock trigger) on " \
                          "backend: %s index: %s" % \
                          (index.backend_id.display_name, index.display_name)
            if variants_index:
                self.with_delay(
                    description=description)._product_stock_update_by_index(
                    variants_index, mapper)

    @api.model
    def _get_shopinvader_variants_from_product(self, products):
        """
        Extract shopinvader.variant from given product.product.
        Get only variants of product binded and only if the stock value
        has been updated since last sync
        :param products: product.product recordset
        :return: shopinvader.variant recordset
        """
        precision = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')
        products = products.filtered(
            lambda p: p.is_shopinvader_binded).with_prefetch(self._prefetch)
        # Get every shopinvader variant where the backend has a json key to
        # export
        shopinvader_variants = products.shopinvader_bind_ids.filtered(
            lambda v: v.se_backend_id.export_stock_key)
        shopinvader_variants = shopinvader_variants.with_prefetch(
            self._prefetch)
        # Get every shopinvader variant where the quantity has been updated
        shopinvader_variants = shopinvader_variants.filtered(
            lambda v:
            float_compare(v._get_se_backend_stock_value(),
                          v.last_stock_value, precision_digits=precision) != 0)
        shopinvader_variants = shopinvader_variants.with_prefetch(
            self._prefetch)
        return shopinvader_variants

    @api.multi
    @job(default_channel='root.search_engine')
    def _product_stock_update_by_index(self, shopinvader_variants, mapper):
        """
        Job to export shopinvader.variant by index
        :param shopinvader_variants: shopinvader.variant recordset
        :param mapper: str
        :return:
        """
        index = shopinvader_variants.mapped("index_id")
        # We should have only 1 index, not more, not less
        if len(index) != 1:
            message = _("Something wrong happens.\n"
                        "We should have exactly 1 index to export!")
            raise exceptions.MissingError(message)
        backend = index.backend_id.specific_backend
        model_name = first(shopinvader_variants)._name
        with backend.work_on(model_name, index=index) as work:
            exporter = work.component(usage='se.record.exporter')
            # Update the quantity synchronized
            for shopinvader_variant in shopinvader_variants:
                stock_value = shopinvader_variant._get_se_backend_stock_value()
                shopinvader_variant._update_stock_qty_sent(stock_value)
            return exporter.run(shopinvader_variants, mapper=mapper)
