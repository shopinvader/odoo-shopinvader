# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.addons.connector.connector import ConnectorEnvironment


def get_environment(session, model_name, backend_id):
    """ Create an environment to work with. """
    backend_record = session.env['locomotive.backend'].browse(backend_id)
    return ConnectorEnvironment(backend_record, session, model_name)
