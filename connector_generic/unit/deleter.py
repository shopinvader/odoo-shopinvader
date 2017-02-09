# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tools.translate import _
from openerp.addons.connector.unit.synchronizer import Deleter


class GenericDeleter(Deleter):
    """ Base deleter for External System """

    def run(self, external_id):
        """ Run the synchronization, delete the record on an External System
        :param external_id: identifier of the record to delete
        """
        self.backend_adapter.delete(external_id)
        return _('Record %s deleted on %s') % (
            external_id, self.backend_record.name)
