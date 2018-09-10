# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ShopinvaderBackend(models.Model):
    _name = 'shopinvader.backend'

    name = fields.Char(
        required=True
    )
    company_id = fields.Many2one(
        'res.company',
        'Company',
        required=True,
        default=lambda s: s._default_company_id()
    )
    location = fields.Char()
    notification_ids = fields.One2many(
        'shopinvader.notification',
        'backend_id',
        'Notification')
    nbr_product = fields.Integer(compute='_compute_nbr_content')
    nbr_variant = fields.Integer(compute='_compute_nbr_content')
    nbr_category = fields.Integer(compute='_compute_nbr_content')
    last_step_id = fields.Many2one(
        'shopinvader.cart.step',
        string='Last cart step',
        required=True,
        default=lambda s: s._default_last_step_id())
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
    pricelist_id = fields.Many2one(
        'product.pricelist',
        string='Pricelist')

    account_analytic_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Analytic account',
        help='This analytic account will be used to fill the '
             'field on the sale order created.'
    )
    filter_ids = fields.Many2many(
        comodel_name='product.filter',
        string='Filter')

    _sql_constraints = [
        ('auth_api_key_id_uniq', 'unique(auth_api_key_id)',
         'An authentication API Key can be used by one backend.'),
    ]

    @api.model
    def _default_company_id(self):
        return self.env['res.company']._company_default_get(
            'shopinvader.backend')

    @api.model
    def _default_last_step_id(self):
        last_step = self.env['shopinvader.cart.step'].browse()
        try:
            last_step = self.env.ref('shopinvader.cart_end')
        except ValueError:
            pass
        return last_step

    def _to_compute_nbr_content(self):
        """
        Get a dict to compute the number of content.
        The dict is build like this:
        Key = Odoo number fields string (should be Integer/Float)
        Value = The target model string
        :return: dict
        """
        values = {
            # key => Odoo field: value => related model
            'nbr_product': 'shopinvader.product',
            'nbr_category': 'shopinvader.category',
            'nbr_variant': 'shopinvader.variant',
        }
        return values

    def _compute_nbr_content(self):
        to_count = self._to_compute_nbr_content()
        domain = [
            ('backend_id', 'in', self.ids)
        ]
        for odoo_field, odoo_model in to_count.iteritems():
            if odoo_model in self.env and self.env[odoo_model]._table_exist():
                target_model_obj = self.env[odoo_model]
                result = target_model_obj.read_group(
                    domain, ['backend_id'], ['backend_id'], lazy=False)
                result = dict((data['backend_id'][0], data['__count'])
                              for data in result)
                for record in self:
                    record[odoo_field] = result.get(record.id, 0)

    def _bind_all_content(self, model, bind_model, domain):
        for backend in self:
            for lang_id in self.lang_ids:
                for record in self.env[model].search(domain):
                    if not self.env[bind_model].search([
                            ('backend_id', '=', backend.id),
                            ('record_id', '=', record.id),
                            ('lang_id', '=', lang_id.id)]):
                        self.env[bind_model].with_context(
                            map_children=True).create({
                                'backend_id': backend.id,
                                'record_id': record.id,
                                'lang_id': lang_id.id})
        return True

    @api.multi
    def bind_all_product(self):
        return self._bind_all_content(
            'product.template',
            'shopinvader.product',
            [('sale_ok', '=', True)])

    @api.multi
    def bind_all_category(self):
        self._bind_all_content(
            'product.category',
            'shopinvader.category',
            [])

    def _send_notification(self, notification, record):
        self.ensure_one()
        record.ensure_one()
        notif = self.env['shopinvader.notification'].search([
            ('backend_id', '=', self.id),
            ('notification_type', '=', notification),
            ])
        if notif:
            notif.with_delay().send(record.id)
        return True

    def _extract_configuration(self):
        return {}
