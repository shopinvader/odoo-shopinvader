# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openerp.addons.connector_locomotivecms.backend import locomotive
from openerp.addons.shoptor.unit.exporter import ProductExporter, CategExporter

import logging

_logger = logging.getLogger(__name__)

try:
    from algoliasearch import algoliasearch
except ImportError:
    _logger.debug('Can not import algoliasearch')


@locomotive(replacing=ProductExporter)
class ProductExporterIndex(ProductExporter):

    def _create_data(self, map_record, fields=None, **kwargs):
        self._data = super(ProductExporter, self)._create_data(
            map_record, fields=fields, **kwargs)
        return self._data

    def _build_index_name(self, lang, pricelist):
        return "%s_%s" % (lang, pricelist)

    def _extract_data(self, variant, pricelist):
        # TODO make it more flexible
        res = {k: self._data['data'][k] for k in self._data['data']
               if k != 'variants' and self._data['data'][k]}
        res.update({k: variant[k] for k in variant if k != 'pricelist'
                    if variant[k]})
        res['pricelist'] = variant['pricelist'][pricelist].copy()
        res['objectID'] = res['erp_id']
        return res

    def index_to_algolia(self, datas):
        batch_data = []
        for index_name in datas:
            batch_data.append({
                "action": "addObject",
                "indexName": index_name,
                "body": datas[index_name],
                })
        # TODO the connection part should be move out of here
        # we will need it to automatise the generation of index
        # Also we can read information from algolia and show them
        # into the tab search engine of the locomotive backend
        client = algoliasearch.Client(
            self.backend_record.search_engine_username,
            self.backend_record.search_engine_password)
        client.batch(batch_data)

    def _index_record(self):
        lang = self.binding_record.lang_id.code
        datas = {}
        for variant in self._data['data']['variants']:
            for pricelist in variant['pricelist']:
                index_name = self._build_index_name(lang, pricelist)
                datas[index_name] = self._extract_data(variant, pricelist)
        # TODO we should use a connector unit or something else
        # to be able to connect to elatic, solr, or algolia
        self.index_to_algolia(datas)

    def _after_export(self):
        super(ProductExporterIndex, self)._after_export()
        self._index_record()


@locomotive(replacing=CategExporter)
class CategExporterIndex(CategExporter):

    def _create_data(self, map_record, fields=None, **kwargs):
        self._data = super(CategExporter, self)._create_data(
            map_record, fields=fields, **kwargs)
        return self._data

    def _build_index_name(self, lang):
        return "%s_category" % lang

    def _extract_data(self):
        # TODO make it more flexible
        res = {k: self._data['data'][k] for k in self._data['data']
               if self._data['data'][k]}
        res['objectID'] = self._data['erp_id']
        return res

    def index_to_algolia(self, datas):
        batch_data = []
        for index_name in datas:
            batch_data.append({
                "action": "addObject",
                "indexName": index_name,
                "body": datas[index_name],
                })
        # TODO the connection part should be move out of here
        # we will need it to automatise the generation of index
        # Also we can read information from algolia and show them
        # into the tab search engine of the locomotive backend
        client = algoliasearch.Client(
            self.backend_record.search_engine_username,
            self.backend_record.search_engine_password)
        client.batch(batch_data)

    def _index_record(self):
        lang = self.binding_record.lang_id.code
        index_name = self._build_index_name(lang)
        datas = {index_name: self._extract_data()}
        # TODO we should use a connector unit or something else
        # to be able to connect to elatic, solr, or algolia
        self.index_to_algolia(datas)

    def _after_export(self):
        super(CategExporterIndex, self)._after_export()
        self._index_record()
