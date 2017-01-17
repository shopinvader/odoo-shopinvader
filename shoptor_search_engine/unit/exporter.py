# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openerp.addons.connector_locomotivecms.backend import locomotive
from openerp.addons.shoptor.unit.exporter import ProductExporter
from openerp.addons.connector.queue.job import job
from openerp.addons.connector_search_engine.unit.exporter import (
    export_record_se,
    SeExporter)
from openerp.addons.connector_algolia.backend import algolia
from algoliasearch import algoliasearch


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
               if k != 'variants'})
        res.update({k: variant[k] for k in variant if k != 'pricelist'})
        res['pricelist'] = variant['pricelist'][pricelist].copy()
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
        # TODO FIXME
        lang = self.session.context.get('lang', 'fr_FR')
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
