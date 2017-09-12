# -*- coding: utf-8 -*-
# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models
from openerp.tools.translate import _
from openerp.exceptions import Warning as UserError


class ShopinvaderPartner(models.Model):
    _name = 'shopinvader.partner'
    _description = 'Shopinvader Partner'
    _inherit = 'locomotive.binding'
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
    role_id = fields.Many2one(
        comodel_name='shopinvader.role',
        string='Role',
        compute='_compute_role',
        store=True)

    _sql_constraints = [
        ('record_uniq', 'unique(backend_id, record_id, partner_email)',
         'A partner can only have one binding by backend.'),
        ('email_uniq', 'unique(backend_id, partner_email)',
         'An email must be uniq per backend.'),
    ]

    @api.depends(
        'record_id.country_id', 'country_id',
        'record_id.vat', 'vat',
        'record_id.property_product_pricelist', 'property_product_pricelist')
    def _compute_role(self):
        user_company_id = self.env.user.company_id.id
        fposition_obj = self.env['account.fiscal.position']
        for binding in self:
            role = self.env['shopinvader.role']
            company_id = binding.company_id and binding.company_id.id \
                or user_company_id
            partner = binding.record_id
            fposition_id = fposition_obj.get_fiscal_position(
                company_id, partner.id, delivery_id=partner.id)
            if fposition_id:
                role = self.env['shopinvader.role'].search([
                    ('fiscal_position_ids', '=', fposition_id),
                    ('pricelist_id', '=',
                        partner.property_product_pricelist.id),
                    ('backend_id', '=', binding.backend_id.id)])
            if not role:
                role = self.env['shopinvader.role'].search([
                    ('default', '=', True),
                    ('backend_id', '=', binding.backend_id.id)])
                if not role:
                    raise UserError(_(
                        'No default role found for the backend '
                        '%s' % binding.backend_id.name))
            binding.role_id = role.id

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
                    'partner_shipping_id': cart.partner_shipping_id.id})
        return True
