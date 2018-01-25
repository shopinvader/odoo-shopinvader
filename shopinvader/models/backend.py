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
import json
import yaml
import base64

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


@job
def send_notification(session, model_name, notif_id, record_name, record_id):
    record = session.env[record_name].browse(record_id)
    notif = session.env[model_name].browse(notif_id)
    notif._send(record)
    return 'Notification sent'


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


class LocomotiveBackend(models.Model):
    _inherit = 'locomotive.backend'

    payment_method_ids = fields.One2many(
        'shopinvader.payment',
        'backend_id',
        'Payment Method')
    role_ids = fields.One2many(
        'shopinvader.role',
        'backend_id',
        'Customer Role')
    notification_ids = fields.One2many(
        'shopinvader.notification',
        'backend_id',
        'Notification')
    odoo_api = fields.Char(
        help=("This is the API key that you need to add in your website in "
              "order to give the posibility to shopinvader to access to odoo"))
    version = fields.Selection(selection_add=[
        ('shopinvader_v1', 'Shopinvader V1')])
    product_image_resize_ids = fields.Many2many(
        comodel_name='image.resize',
        relation="product_image_resize",
        string='Product Image Resize')
    categ_image_resize_ids = fields.Many2many(
        comodel_name='image.resize',
        relation="category_image_resize",
        string='Category Image Resize')
    nbr_product = fields.Integer(compute='_compute_nbr_content')
    nbr_variant = fields.Integer(compute='_compute_nbr_content')
    nbr_category = fields.Integer(compute='_compute_nbr_content')
    last_step_id = fields.Many2one(
        'shopinvader.cart.step',
        string='Last cart step',
        required=True)
    restrict_anonymous = fields.Boolean(
        help=("Tic that box if yo don't want to forbid an existing customer "
              "to create a sale order in anonymous mode"))
    allowed_country_ids = fields.Many2many(
        comodel_name='res.country',
        string='Allowed Country')
    anonymous_partner_id = fields.Many2one(
        'res.partner',
        'Anonymous Partner',
        required=True,
        default=lambda self: self.env.ref('shopinvader.anonymous'))
    sequence_id = fields.Many2one(
        'ir.sequence',
        'Sequence')

    def _compute_nbr_content(self):
        for record in self:
            for key in ['product', 'category', 'variant']:
                record['nbr_%s' % key] = self.env['shopinvader.%s' % key]\
                    .search_count([('backend_id', '=', record.id)])

    def _export_all_content(self, model):
        session = ConnectorSession.from_env(self.env)
        for record in self:
            bindings = self.env[model]\
                .search([('backend_id', '=', record.id)])
            for binding in bindings:
                delay_export(session, model, binding.id, {})
        return True

    def _clear_dead_locomotive_content(self, model):
        """This method will check the existing product on shopinvader site
        and delete it if it does not exist in odoo. This is really usefull
        in dev mode and can be usefull if you have done some mistake in your
        database production."""
        session = ConnectorSession.from_env(self.env)
        for record in self:
            clear_dead_content.delay(session, model, record.id)
        return True

    def _bind_all_content(self, model, bind_model, domain):
        for backend in self:
            for record in self.env[model].search(domain):
                if not self.env[bind_model].search([
                        ('backend_id', '=', backend.id),
                        ('lang_id', '=', backend.lang_ids[0].id),
                        ('record_id', '=', record.id)]):
                    self.env[bind_model].create({
                        'backend_id': backend.id,
                        'lang_id': backend.lang_ids[0].id,
                        'record_id': record.id})
        return True

    @api.multi
    def bind_all_product(self):
        return self._bind_all_content(
            'product.template',
            'shopinvader.product',
            [('sale_ok', '=', True)])

    @api.multi
    def bind_all_category(self):
        self.with_context(recompute=False)._bind_all_content(
            'product.category',
            'shopinvader.category',
            [])
        self.recompute()

    def _send_notification(self, notification, record):
        self.ensure_one()
        record.ensure_one()
        notif = self.env['shopinvader.notification'].search([
            ('backend_id', '=', self.id),
            ('notification_type', '=', notification),
            ])
        if notif:
            session = ConnectorSession.from_env(self.env)
            send_notification.delay(
                session, notif._name, notif.id, record._name, record.id)
        return True

    def _extract_configuration(self):
        return {}

    def _extract_json_configuration(self):
        config = self._extract_configuration()
        for key in config:
            config[key] = json.dumps(
                config[key], sort_keys=True,
                indent=4, encoding='utf-8',
                separators=(',', ':'))
        return config

    @api.multi
    def export_store_configuration(self):
        self.ensure_one()
        config = self._extract_json_configuration()
        fp = StringIO()
        fp.write(yaml.dump(
            {'_store': config},
            encoding='utf-8',
            default_style='>'))
        fp.seek(0)
        data = base64.b64encode(fp.read())
        wizard = self.env['shopinvader.store.config'].create({
            'data': data,
            'filename': 'site.yml',
            })
        action = self.env.ref(
            'shopinvader.act_open_shopinvader_store_config_view').read()[0]
        action['res_id'] = wizard.id
        return action
