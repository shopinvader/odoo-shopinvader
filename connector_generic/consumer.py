# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# @author Benoit Guillot <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


import logging
from openerp.addons.connector.connector import Binder
from openerp.addons.connector.unit.mapper import ExportMapper

_logger = logging.getLogger(__name__)


class Consumer(object):

    def __init__(self, session, get_environment, model_name, record_id):
        self.session = session
        self.get_environment = get_environment
        self.record = self.session.env[model_name].browse(record_id)

    def get_env(self):
        return self.get_environment(
            self.session, self.record._name, self.record.backend_id.id)

    def _force_export(self):
        return self.session.context.get('connector_force_export')

    def _skip_export(self):
        return self.session.context.get('connector_no_export')

    def with_record(self, record):
        return Consumer(
            self.session, self.get_environment, record._name, record.id)

    def _need_to_export(self, fields=None):
        if self._force_export():
            return True
        env = self.get_env()
        mapper = env.get_connector_unit(ExportMapper)
        exported_fields = mapper.get_changed_by_fields()
        if fields:
            if not exported_fields & set(fields):
                _logger.debug(
                    "Skip export of %s because modified fields: %s are not part "
                    "of exported fields %s",
                    self.record._name, fields, list(exported_fields))
                return False
        return True

    def delay_export(self, export_method, vals):
        """ Delay a job which export a binding record.__package__
        (A binding record being a ``external.res.partner``,
        ``external.product.product``, ...)
        """
        if self._skip_export():
            return
        fields = vals.keys()
        if not self._need_to_export(fields=fields):
            return
        export_method.delay(
            self.session, self.record._name, self.record.id, fields=fields)

    def delay_export_all_binding(self, export_method, binding_key, vals):
        """ Delay a job which export all the bindings of a record.

        In this case, it is called on records of normal models and will delay
        the export for all the bindings.
        """
        for binding in self.record[binding_key]:
            self.with_record(binding).delay_export(export_method, vals)

    def delay_unlink(self, export_delete_method):
        """ Delay a job which delete a record on Prestashop.

        Called on binding records."""
        env = self.get_env()
        binder = env.get_connector_unit(Binder)
        external_id = binder.to_backend(self.record.id)
        if external_id:
            export_delete_method.delay(self.session, self.record._name,
                                       self.record.backend_id.id, external_id)

    def delay_unlink_all_binding(self, export_delete_method, binding_key):
        """ Delay a job which delete a record on an external system.
        Called on binding records."""
        for bind_record in self.record[binding_key]:
            self.with_record(bind_record).delay_unlink(export_delete_method)
