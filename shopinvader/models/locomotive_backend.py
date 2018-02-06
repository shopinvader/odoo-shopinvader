# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


# TODO TO MIGRATE
# @job
# def send_notification(session, model_name, notif_id, record_name, record_id):
#     record = session.env[record_name].browse(record_id)
#     notif = session.env[model_name].browse(notif_id)
#     notif._send(record)
#     return 'Notification sent'
#
#
# @job
# def clear_dead_content(session, model_name, backend_id):
#     env = get_environment(session, model_name, backend_id)
#     adapter = env.get_connector_unit(CRUDAdapter)
#     binder = env.get_connector_unit(Binder)
#     page = 1
#     while True:
#         data = adapter.search(page=page)
#         if not data:
#             break
#         page += 1
#         for content in data:
#             if not binder.to_odoo(content['_id']):
#                 export_delete_record.delay(
#                     session, model_name, backend_id, content['_id'])


class LocomotiveBackend(models.Model):
    _inherit = 'locomotive.backend'
    role_ids = fields.One2many(
        'shopinvader.role',
        'backend_id',
        'Customer Role')
    notification_ids = fields.One2many(
        'shopinvader.notification',
        'backend_id',
        'Notification')
    # TODO move to shopinvader_image
    # product_image_resize_ids = fields.Many2many(
    #    comodel_name='image.resize',
    #    relation="product_image_resize",
    #    string='Product Image Resize')
    # categ_image_resize_ids = fields.Many2many(
    #    comodel_name='image.resize',
    #    relation="category_image_resize",
    #    string='Category Image Resize')
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
    auth_api_key_id = fields.Many2one(
        'auth.api.key',
        required=True,
    )
    lang_ids = fields.Many2many(
        'res.lang',
        string='Lang',
        required=True)

    _sql_constraints = [
        ('auth_api_key_id_uniq', 'unique(auth_api_key_id)',
         'An authentication API Key can be used by one backend.'),
    ]

    def _compute_nbr_content(self):
        for record in self:
            for key in ['product', 'category', 'variant']:
                record['nbr_%s' % key] = self.env['shopinvader.%s' % key]\
                    .search_count([('backend_id', '=', record.id)])

    def _export_all_content(self, model):
        pass
        # TODO Migrate
        # session = ConnectorSession.from_env(self.env)
        # for record in self:
        #     bindings = self.env[model]\
        #         .search([('backend_id', '=', record.id)])
        #     for binding in bindings:
        #         delay_export(session, model, binding.id, {})
        # return True

    def _clear_dead_locomotive_content(self, model):
        pass
        # TODO Migrate
        # """This method will check the existing product on shopinvader site
        # and delete it if it does not exist in odoo. This is really usefull
        # in dev mode and can be usefull if you have done some mistake in your
        # database production."""
        # session = ConnectorSession.from_env(self.env)
        # for record in self:
        #     clear_dead_content.delay(session, model, record.id)
        # return True

    def _bind_all_content(self, model, bind_model, domain):
        for backend in self:
            for record in self.env[model].search(domain):
                if not self.env[bind_model].search([
                        ('backend_id', '=', backend.id),
                        ('record_id', '=', record.id)]):
                    self.env[bind_model].with_context(
                        map_children=True).create({
                        'backend_id': backend.id,
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
        pass
        # TODO Migrate
        # self.ensure_one()
        # record.ensure_one()
        # notif = self.env['shopinvader.notification'].search([
        #     ('backend_id', '=', self.id),
        #     ('notification_type', '=', notification),
        #     ])
        # if notif:
        #     session = ConnectorSession.from_env(self.env)
        #     send_notification.delay(
        #         session, notif._name, notif.id, record._name, record.id)
        # return True

    def _extract_configuration(self):
        return {}

    @api.multi
    def export_store_configuration(self):
        self.ensure_one()
        config = self._extract_configuration()
        return ('test', '.csv')

