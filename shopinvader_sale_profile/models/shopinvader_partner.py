# Copyright 2018 Akretion (http://www.akretion.com).
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, exceptions, fields, models
from odoo.fields import first


class ShopinvaderPartner(models.Model):
    _inherit = "shopinvader.partner"

    sale_profile_id = fields.Many2one(
        "shopinvader.sale.profile",
        "Sale profile",
        compute="_compute_sale_profile_id",
        store=True,
        help="Sale profile computed, depending every fields who make the "
        "fiscal position (country, zip, vat, account position,...)",
    )

    def _compute_role_depends(self):
        return super()._compute_role_depends() + (
            "backend_id.use_sale_profile",
            "sale_profile_id",
        )

    def _get_role(self):
        # Override to use the sale profile role/code when required
        role = super()._get_role()
        if self.backend_id.use_sale_profile and self.sale_profile_id:
            role = self.sale_profile_id.code
        return role

    @api.depends(
        "record_id.country_id",
        "country_id",
        "record_id.vat",
        "vat",
        "record_id.property_product_pricelist",
        "property_product_pricelist",
        "property_account_position_id",
        "state_id",
        "zip",
        "backend_id.use_sale_profile",
        "backend_id.sale_profile_ids",
        "backend_id.company_id",
    )
    def _compute_sale_profile_id(self):
        """Compute function for the field sale_profile_id.

        :return:
        """
        sale_profile_obj = self.env["shopinvader.sale.profile"]
        # Only backends using profiles
        backend_ids = (
            self.mapped("backend_id")
            .filtered(lambda b: b.use_sale_profile)
            .with_prefetch(self._prefetch_ids)
            .ids
        )
        partners = self.mapped("record_id")
        pricelists = partners.mapped("property_product_pricelist")
        default_sale_profiles = self._get_default_profiles(backend_ids)
        # company_id field is mandatory so we don't have manage empty value
        for company in self.mapped("backend_id.company_id"):
            fposition_by_partner = self._get_fiscal_position_by_partner(
                partners, company=company
            )
            # Get every fiscal position ids (without duplicates)
            fposition_ids = list(set(fposition_by_partner.values()))
            sale_profiles = self._get_sale_profiles(
                backend_ids, pricelists, fposition_ids, company
            )
            shopinv_partners = self.filtered(
                lambda p, c=company: p.backend_id.company_id.id == c.id
            )
            shopinv_partners = shopinv_partners.with_company(company)
            for binding in shopinv_partners:
                sale_profile = sale_profile_obj.browse()
                # Only if the related backend use sale profiles
                if binding.backend_id.use_sale_profile:
                    partner = binding.record_id
                    fposition_id = fposition_by_partner.get(partner.id, False)
                    sale_profile = binding._sale_profile_with_backend(
                        default_sale_profiles, fposition_id, sale_profiles
                    )
                binding.sale_profile_id = sale_profile

    def _sale_profile_with_backend(
        self, default_sale_profiles, fposition_id, sale_profiles
    ):
        """Get sale profile of current recordset.

        Look it up based on default sale profiles given in parameters,
        fiscal position id and every related profile of related backend

        :param default_sale_profiles: shopinvader.sale.profile recordset
        :param fposition_id: int
        :param sale_profiles: shopinvader.sale.profile recordset
        :return: shopinvader.sale.profile recordset
        """
        self.ensure_one()
        sale_profile = self.env["shopinvader.sale.profile"].browse()
        partner = self.record_id
        backend = self.backend_id
        if fposition_id:
            # Get the sale profile using the fiscal position, pricelist,...
            pricelist = partner.property_product_pricelist
            sale_profile = sale_profiles.filtered(
                lambda p, fpos=fposition_id, pl=pricelist, b=backend: fpos
                in p.fiscal_position_ids.ids
                and p.pricelist_id.id == pl.id
                and p.backend_id.id == b.id
            )
            sale_profile = first(sale_profile.with_prefetch(self._prefetch_ids))
        else:
            pricelist = partner.property_product_pricelist
            sale_profile = sale_profiles.filtered(
                lambda p, pl=pricelist, b=backend: not p.fiscal_position_ids
                and p.pricelist_id.id == pl.id
                and p.backend_id.id == b.id
            )
            sale_profile = first(sale_profile.with_prefetch(self._prefetch_ids))
        if not sale_profile:
            # Get the default sale profile
            sale_profile = default_sale_profiles.filtered(
                lambda p, b=backend: p.backend_id.id == b.id
            )
            sale_profile = first(sale_profile.with_prefetch(self._prefetch_ids))
            if not sale_profile:
                message = (
                    _("No default sale profile found for the backend" " %s")
                    % self.backend_id.name
                )
                raise exceptions.UserError(message)
        return sale_profile

    def _get_sale_profiles(self, backend_ids, pricelists, fposition_ids, company=False):
        """Get sale profiles for given backends, fiscal positions, pricelists.

        :param fposition_ids: list of int
        :param backend_ids: list of int
        :param pricelists: product.pricelist recordset
        :param company: res.company recordset
        :return: shopinvader.sale.profile recordset
        """
        sale_profile_obj = self.env["shopinvader.sale.profile"]
        if company:
            sale_profile_obj = sale_profile_obj.with_company(company)
        domain = [
            "|",
            ("fiscal_position_ids", "in", fposition_ids),
            ("fiscal_position_ids", "=", False),
            ("pricelist_id", "in", pricelists.ids),
            ("backend_id", "in", backend_ids),
        ]
        sale_profiles = sale_profile_obj.search(domain)
        return sale_profiles

    @api.model
    def _get_default_profiles(self, backend_ids):
        """Get every default profile for given backend IDS.

        :param backend_ids: list of int
        :return: shopinvader.sale.profile recordset
        """
        sale_profile_obj = self.env["shopinvader.sale.profile"]
        domain_default_profiles = [
            ("default", "=", True),
            ("backend_id", "in", backend_ids),
        ]
        default_sale_profiles = sale_profile_obj.search(domain_default_profiles)
        return default_sale_profiles

    @api.model
    def _get_fiscal_position_by_partner(self, partners, company=False):
        """Get every fiscal position related to given partners.

        :param partners: res.partner recordset
        :param company_id: int
        :return: account.fiscal.position recordset
        """
        fposition_obj = self.env["account.fiscal.position"]
        if company:
            fposition_obj = fposition_obj.with_company(company)
        fposition_by_partner = {}
        for partner in partners:
            fpos = fposition_obj.get_fiscal_position(partner.id, delivery_id=partner.id)
            if fpos:
                fposition_by_partner[partner.id] = fpos.id
        return fposition_by_partner
