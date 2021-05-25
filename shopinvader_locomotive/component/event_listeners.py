# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component
from odoo.addons.component_event import skip_if


class ShopinvaderBindingListener(Component):
    _name = "shopinvader.binding.event.listener"
    _inherit = "base.connector.listener"

    _apply_on = ["shopinvader.partner"]

    @skip_if(lambda self, record, **kwargs: self.no_connector_export(record))
    def on_record_create(self, record, fields=None):
        record.with_delay().export_record(_fields=fields)

    @skip_if(lambda self, record, **kwargs: self.no_connector_export(record))
    def on_record_write(self, record, fields=None):
        record.with_delay().export_record(_fields=fields)

    def on_record_unlink(self, record):
        with record.backend_id.work_on(record._name) as work:
            external_id = work.component(usage="binder").to_external(record)
            if external_id:
                record.with_delay().export_delete_record(record.backend_id, external_id)


class ShopinvaderRecordListener(Component):
    _name = "shopinvader.record.event.listener"
    _inherit = "base.connector.listener"

    _apply_on = ["res.partner"]

    def _get_fields_to_export(self):
        return ["name", "email"]

    @skip_if(lambda self, record, **kwargs: self.no_connector_export(record))
    def on_record_write(self, record, fields=None):
        fields_to_export = self._get_fields_to_export()
        if not set(fields_to_export).intersection(set(fields)):
            return
        if "shopinvader_bind_ids" not in record._fields:
            return
        for binding in record._get_binding_to_export():
            binding.with_delay().export_record(_fields=fields)

    def on_record_unlink(self, record, fields=None):
        """Unlink all binding before removing the record in order to
        trigger an event for deleting the record in locomotive"""
        if "shopinvader_bind_ids" not in record._fields:
            return
        for binding in record.shopinvader_bind_ids:
            binding.unlink()
