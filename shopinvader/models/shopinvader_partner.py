# -*- coding: utf-8 -*-
# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ShopinvaderPartner(models.Model):
    _name = 'shopinvader.partner'
    _description = 'Shopinvader Partner'
    _inherit = 'shopinvader.binding'
    _inherits = {'res.partner': 'record_id'}

    record_id = fields.Many2one(
        'res.partner',
        required=True,
        ondelete='cascade')
    partner_email = fields.Char(
        related='record_id.email',
        readonly=True,
        required=True,
        store=True)

    _sql_constraints = [
        ('record_uniq', 'unique(backend_id, record_id, partner_email)',
         'A partner can only have one binding by backend.'),
        ('email_uniq', 'unique(backend_id, partner_email)',
         'An email must be uniq per backend.'),
    ]

    @api.model
    def create(self, vals):
        # As we want to have a SQL contraint on customer email
        # we have to set it manually to avoid to raise the constraint
        # at the creation of the element
        vals['partner_email'] = self.env['res.partner'].browse(
            vals['record_id']).email
        return super(ShopinvaderPartner, self).create(vals)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    shopinvader_bind_ids = fields.One2many(
        'shopinvader.partner',
        'record_id',
        string='Shopinvader Binding')
    address_type = fields.Selection(
        selection=[('profile', 'Profile'), ('address', 'Address')],
        string='Address Type',
        compute='_compute_address_type',
        store=True)
    # In europe we use more the opt_in
    opt_in = fields.Boolean(
        compute='_compute_opt_in',
        inverse='_inverse_opt_in')

    @api.depends('opt_out')
    def _compute_opt_in(self):
        for record in self:
            record.opt_in = not record.opt_out

    def _inverse_opt_in(self):
        for record in self:
            record.opt_out = not record.opt_in

    @api.depends('parent_id')
    def _compute_address_type(self):
        for partner in self:
            if partner.parent_id:
                partner.address_type = 'address'
            else:
                partner.address_type = 'profile'

    @api.multi
    def write(self, vals):
        super(ResPartner, self).write(vals)
        if 'country_id' in vals:
            carts = self.env['sale.order'].search([
                ('typology', '=', 'cart'),
                ('partner_shipping_id', 'in', self.ids)])
            for cart in carts:
                # Trigger a write on cart to recompute the
                # fiscal position if needed
                cart.write_with_onchange({
                    'partner_shipping_id': cart.partner_shipping_id.id,
                    })
        return True
