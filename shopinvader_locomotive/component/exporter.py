# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.component.core import Component


class LocomotiveExporter(Component):
    _name = 'locomotive.exporter'
    _inherit = ['generic.exporter', 'base.locomotive.connector']
    _usage = 'record.exporter'

    def _update_data(self, map_record, fields=None, **kwargs):
        """ Get the data to pass to :py:meth:`_update` """
        # As we push a json we always need to push all info
        return self._create_data(map_record, fields=None, **kwargs)

    def _create(self, record):
        result = super(LocomotiveExporter, self)._create(record)
        return result['_id']
