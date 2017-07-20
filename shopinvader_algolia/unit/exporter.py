# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp.addons.connector.queue.job import job
from openerp.addons.connector_search_engine.unit.exporter import (
    export_record_se,
    SeExporter)
from openerp.addons.connector_algolia.backend import algolia


@job(default_channel='root.shopinvader.catalog')
def export_record(session, model_name, binding_ids):
    return export_record_se(session, model_name, binding_ids)


@algolia
class AlgoliaExporter(SeExporter):
    _model_name = [
        'shopinvader.variant',
        'shopinvader.category',
        ]

    def get_export_func(self):
        """ Should return the delay export func of the binding """
        return export_record
