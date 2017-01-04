# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openerp.addons.connector_generic.unit.exporter import GenericExporter
from ..related_action import unwrap_binding
from openerp.addons.connector.queue.job import job, related_action
from ..connector import get_environment


class LocomotivecmsExporter(GenericExporter):
    _default_binding_fields = 'locomotivecms_bind_ids'

    def _update_data(self, map_record, fields=None, **kwargs):
        """ Get the data to pass to :py:meth:`_update` """
        # As we push a json we always need to push all info
        return self._create_data(map_record, fields=None, **kwargs)


@job(default_channel='root.locomotive')
@related_action(action=unwrap_binding)
def export_record(session, model_name, binding_id, fields=None):
    """ Export a record on LocomotiveCMS """
    record = session.env[model_name].browse(binding_id)
    env = get_environment(session, model_name, record.backend_id.id)
    exporter = env.get_connector_unit(GenericExporter)
    return exporter.run(binding_id, fields=fields)
