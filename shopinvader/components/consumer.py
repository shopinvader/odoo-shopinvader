# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component
from odoo.addons.component_event import skip_if


class ShopinvaderBindingListener(Component):
    _name = 'shopinvader.binding.event.listener'
    _inherit = 'base.connector.listener'

    _apply_on = [
        'shopinvader.partner',
        ]

    @skip_if(lambda self, record, **kwargs: self.no_connector_export(record))
    def on_record_create(self, record, fields=None):
        record.with_delay().export_record(fields=fields)

    @skip_if(lambda self, record, **kwargs: self.no_connector_export(record))
    def on_record_write(self, record, fields=None):
        record.with_delay().export_record(fields=fields)

    def on_record_unlink(self, record):
        with record.backend_id.work_on(record._name) as work:
            external_id = work.component(usage='binder').to_external(record)
            if external_id:
                record.with_delay().export_delete_record(record.backend_id,
                                                         external_id)


class ShopinvaderRecordListener(Component):
    _name = 'shopinvader.record.event.listener'
    _inherit = 'base.connector.listener'

    _apply_on = [
        'res.partner',
        ]

    @skip_if(lambda self, record, **kwargs: self.no_connector_export(record))
    def on_record_write(self, record, fields=None):
        """ Called when a record is updated """
        if fields == ['shopinvader_bind_ids']:
            return
        for binding in record.shopinvader_bind_ids:
            binding.with_delay().export_record(fields=fields)

    @skip_if(lambda self, record, **kwargs: self.no_connector_export(record))
    def on_record_unlink(self, record, fields=None):
        """ Called when a record is unlink """
        for binding in record.shopinvader_bind_ids:
            binding.with_delay().delete_record(fields=fields)
