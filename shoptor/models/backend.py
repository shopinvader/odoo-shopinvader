# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models
from openerp.addons.connector.queue.job import job
from openerp.addons.connector.unit.backend_adapter import CRUDAdapter
from openerp.addons.connector.connector import Binder
from openerp.addons.connector_locomotivecms.unit.deleter import (
    export_delete_record)
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.connector_locomotivecms.connector import get_environment
from ..unit.consumer import delay_export


@job
def clear_dead_content(session, model_name, backend_id):
    env = get_environment(session, model_name, backend_id)
    adapter = env.get_connector_unit(CRUDAdapter)
    binder = env.get_connector_unit(Binder)
    page = 1
    while True:
        data = adapter.search(page=page)
        if not data:
            break
        page += 1
        for content in data:
            if not binder.to_openerp(content['_id']):
                export_delete_record.delay(
                    session, model_name, backend_id, content['_id'])


class LocomotivecmsBackend(models.Model):
    _inherit = 'locomotivecms.backend'

    pricelist_ids = fields.One2many(
        'locomotivecms.pricelist',
        'backend_id',
        'Pricelist')
    odoo_api = fields.Char(
        help=("This is the API key that you need to add in your website in "
              "order to give the posibility to locomotive to access to odoo"))
    nbr_product = fields.Integer(compute='_compute_nbr_product')

    def _compute_nbr_product(self):
        for record in self:
            record.nbr_product = self.env['locomotivecms.product']\
                .search_count([('backend_id', '=', record.id)])

    @api.multi
    def clear_dead_product(self):
        """This method will check the existing product on locomotive site
        and delete it if not do not exist in odoo. This is really usefull
        in dev mode and can be usefull if you have done some mistake in your
        database production."""
        session = ConnectorSession.from_env(self.env)
        for record in self:
            return clear_dead_content.delay(
                session, 'locomotivecms.product', record.id)
        return True

    @api.multi
    def export_all_product(self):
        session = ConnectorSession.from_env(self.env)
        for record in self:
            bindings = self.env['locomotivecms.product']\
                .search([('backend_id', '=', record.id)])
            for binding in bindings:
                delay_export(session, 'locomotivecms.product', binding.id, {})
        return True
