# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, exceptions, fields, models, _
from odoo.fields import first


class ShopinvaderPartner(models.Model):
    _inherit = 'shopinvader.partner'

    sale_profile_id = fields.Many2one(
        'shopinvader.sale.profile',
        'Sale profile',
        compute='_compute_sale_profile_id',
        store=True,
        help="Sale profile computed, depending every fields who make the "
             "fiscal position (country, zip, vat, account position,...)",
    )

    @api.multi
    @api.depends(
        'record_id.country_id', 'country_id', 'record_id.vat', 'vat',
        'record_id.property_product_pricelist', 'property_product_pricelist',
        'property_account_position_id', 'state_id', 'zip',
        'backend_id.use_sale_profile', 'backend_id.sale_profile_ids')
    def _compute_sale_profile_id(self):
        """
        Compute function for the field sale_profile_id.
        :return:
        """
        sale_profile_obj = self.env['shopinvader.sale.profile']
        # Only backends using profiles
        backend_ids = self.mapped("backend_id").filtered(
            lambda b: b.use_sale_profile).with_prefetch(self._prefetch).ids
        partners = self.mapped("record_id")
        pricelists = partners.mapped("property_product_pricelist")
        fposition_by_partner = self._get_fiscal_position_by_partner(partners)
        # Get every fiscal position ids (without duplicates)
        fposition_ids = list(set(fposition_by_partner.values()))
        default_sale_profiles = self._get_default_profiles(backend_ids)
        sale_profiles = self._get_sale_profiles(
            backend_ids, pricelists, fposition_ids)
        for binding in self:
            sale_profile = sale_profile_obj.browse()
            # Only if the related backend use sale profiles
            if binding.backend_id.use_sale_profile:
                partner = binding.record_id
                fposition_id = fposition_by_partner.get(partner.id, False)
                sale_profile = binding._sale_profile_with_backend(
                    default_sale_profiles, fposition_id, sale_profiles)
            binding.sale_profile_id = sale_profile

    @api.multi
    def _sale_profile_with_backend(self, default_sale_profiles,
                                   fposition_id, sale_profiles):
        """
        Get the sale profile of current recordset based on default
        sale profiles given in parameters, fiscal position id and
        every related profile of related backend
        :param default_sale_profiles: shopinvader.sale.profile recordset
        :param fposition_id: int
        :param sale_profiles: shopinvader.sale.profile recordset
        :return: shopinvader.sale.profile recordset
        """
        self.ensure_one()
        sale_profile = self.env['shopinvader.sale.profile'].browse()
        partner = self.record_id
        backend = self.backend_id
        if fposition_id:
            # Get the sale profile using the fiscal position, pricelist,...
            pricelist = partner.property_product_pricelist
            sale_profile = sale_profiles.filtered(
                lambda p, fpos=fposition_id, pl=pricelist, b=backend:
                fpos in p.fiscal_position_ids.ids and
                p.pricelist_id.id == pl.id and p.backend_id.id == b.id)
            sale_profile = first(sale_profile.with_prefetch(self._prefetch))
        if not sale_profile:
            # Get the default sale profile
            sale_profile = default_sale_profiles.filtered(
                lambda p, b=backend: p.backend_id.id == b.id)
            sale_profile = first(
                sale_profile.with_prefetch(self._prefetch))
            if not sale_profile:
                message = _('No default sale profile found for the backend'
                            ' %s') % self.backend_id.name
                raise exceptions.UserError(message)
        return sale_profile

    def _get_sale_profiles(self, backend_ids, pricelists, fposition_ids):
        """
        Get every shopinvader.sale.profile related to given backend,
        fiscal position and pricelists.
        :param fposition_ids: list of int
        :param backend_ids: list of int
        :param pricelists: product.pricelist recordset
        :return: shopinvader.sale.profile recordset
        """
        sale_profile_obj = self.env['shopinvader.sale.profile']
        domain = [
            ('fiscal_position_ids', 'in', fposition_ids),
            ('pricelist_id', 'in', pricelists.ids),
            ('backend_id', 'in', backend_ids),
        ]
        sale_profiles = sale_profile_obj.search(domain)
        return sale_profiles

    @api.model
    def _get_default_profiles(self, backend_ids):
        """
        Get every default profile for given backend
        :param backend_ids: list of int
        :return: shopinvader.sale.profile recordset
        """
        sale_profile_obj = self.env['shopinvader.sale.profile']
        domain_default_profiles = [
            ('default', '=', True),
            ('backend_id', 'in', backend_ids),
        ]
        default_sale_profiles = sale_profile_obj.search(
            domain_default_profiles)
        return default_sale_profiles

    @api.model
    def _get_fiscal_position_by_partner(self, partners):
        """
        Get every fiscal position related to given partners
        :param partners: res.partner recordset
        :return: account.fiscal.position recordset
        """
        fposition_obj = self.env['account.fiscal.position']
        fposition_by_partner = {}
        for partner in partners:
            fpos_id = fposition_obj.get_fiscal_position(
                partner.id, delivery_id=partner.id)
            if fpos_id:
                fposition_by_partner.update({
                    partner.id: fpos_id,
                })
        return fposition_by_partner
