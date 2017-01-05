# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openerp.addons.connector_generic.unit.exporter import GenericExporter
from ..related_action import unwrap_binding
from openerp.addons.connector.queue.job import job, related_action
from ..connector import get_environment
from openerp.tools.translate import _


class LocomotivecmsExporter(GenericExporter):
    _default_binding_fields = 'locomotivecms_bind_ids'

    def _update_data(self, map_record, fields=None, **kwargs):
        """ Get the data to pass to :py:meth:`_update` """
        # As we push a json we always need to push all info
        return self._create_data(map_record, fields=None, **kwargs)

    def _run(self, fields=None):
        """ Flow of the synchronization, implemented in inherited classes"""
        assert self.binding_id
        assert self.binding_record

        if not self.external_id:
            fields = None  # should be created with all the fields

        if self._has_to_skip():
            return

        # export the missing linked resources
        self._export_dependencies()

        # prevent other jobs to export the same record
        # will be released on commit (or rollback)
        self._lock()

        map_record = self._map_data()

        if self.external_id:
            record = self._update_data(map_record, fields=fields)
            if not record:
                return _('Nothing to export.')
            self.result = self._update(record)
        else:
            record = self._create_data(map_record, fields=fields)
            if not record:
                return _('Nothing to export.')
            self.result = self._create(record)
            self.external_id = self.result['_id']
        return _('Record exported with ID %s on %s.') % (
	    self.external_id, self.backend_record.name)


@job(default_channel='root.locomotive')
@related_action(action=unwrap_binding)
def export_record(session, model_name, binding_id, fields=None):
    """ Export a record on LocomotiveCMS """
    record = session.env[model_name].browse(binding_id)
    env = get_environment(session, model_name, record.backend_id.id)
    exporter = env.get_connector_unit(GenericExporter)
    return exporter.run(binding_id, fields=fields)
