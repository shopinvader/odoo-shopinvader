# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.component.core import Component
from odoo.tools.translate import _


class LocomotiveExporter(Component):
    _name = 'locomotive.exporter'
    _inherit = ['generic.exporter', 'base.locomotive.connector']
    _usage = 'record.exporter'

    def _update_data(self, map_record, fields=None, **kwargs):
        """ Get the data to pass to :py:meth:`_update` """
        # As we push a json we always need to push all info
        return self._create_data(map_record, fields=None, **kwargs)

    def run(self, record, *args, **kwargs):
        ctx = self.env.context.copy()
        if 'lang_id' in self.model._fields:
            ctx['lang'] = self.model.browse(binding_id).lang_id.code
            self.session.env = self.env(context=ctx)
        return super(LocomotiveExporter, self).run(record, *args, **kwargs)

    def _run(self, fields=None):
        """ Flow of the synchronization, implemented in inherited classes"""
        assert self.binding

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
