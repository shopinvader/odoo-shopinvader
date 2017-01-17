# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.addons.connector.queue.job import job
from openerp.addons.connector_generic.unit.deleter import GenericDeleter
from ..connector import get_environment


class LocomotivecmsDeleter(GenericDeleter):
    """Locomotive Deleter"""


@job(default_channel='root.locomotivecms')
def export_delete_record(session, model_name, backend_id, external_id):
    """ Delete a record on LocomotiveCMS """
    env = get_environment(session, model_name, backend_id)
    deleter = env.get_connector_unit(LocomotivecmsDeleter)
    return deleter.run(external_id)
