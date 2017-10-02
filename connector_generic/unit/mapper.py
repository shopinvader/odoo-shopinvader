# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.connector.unit.mapper import ExportMapper


class GenericExportMapper(ExportMapper):

    def get_changed_by_fields(self):
        """
        You can override this method to add a custom way to consider fields.
        """
        return set(self._changed_by_fields)
