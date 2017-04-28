# -*- coding: utf-8 -*-
# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models
from openerp.tools.translate import _
from openerp.exceptions import Warning as UserError


class LocomotivePartner(models.Model):
    _name = 'locomotive.partner'
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
        comodel_name='locomotive.role',
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
            role = self.env['locomotive.role']
            company_id = binding.company_id and binding.company_id.id \
                or user_company_id
            partner = binding.record_id
            fposition_id = fposition_obj.get_fiscal_position(
                company_id, partner.id, delivery_id=partner.id)
            if fposition_id:
                role = self.env['locomotive.role'].search([
                    ('fiscal_position_ids', 'in', fposition_id),
                    ('backend_id', '=', binding.backend_id.id)])
            if not role:
                role = self.env['locomotive.role'].search([
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
        return super(LocomotivePartner, self).create(vals)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    locomotive_bind_ids = fields.One2many(
        'locomotive.partner',
        'record_id',
        string='Locomotive Binding')
    contact_type = fields.Selection(
        selection=[('profile', 'Profile'), ('address', 'Address')],
        string='Contact Type',
        compute='_compute_contact_type',
        store=True)

    @api.depends('parent_id')
    def _compute_contact_type(self):
        for partner in self:
            if partner.parent_id:
                partner.contact_type = 'address'
            else:
                partner.contact_type = 'profile'
