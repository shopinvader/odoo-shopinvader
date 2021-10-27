# Copyright 2018 Akretion (http://www.akretion.com).
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# Copyright 2021 Camptocamp SA (https://www.camptocamp.com)
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# @author Iván Todorovich <ivan.todorovich@gmail.com>
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
        if self.backend_id.use_sale_profile and self.sale_profile_id:
            return self.sale_profile_id.code
        return super()._get_role()

    @api.model
    def _compute_sale_profile_id_depends(self):
        backend_fields = [
            "backend_id.use_sale_profile",
            "backend_id.sale_profile_ids",
            "backend_id.company_id",
        ]
        # Using `_address_fields` gives us a lazy compatibility
        # with modules like `base_address_city` or `base_location`
        partner_address_fields = [
            f"record_id.{fname}"
            for fname in self.env["res.partner"]._address_fields()
            if not fname.startswith("street")
        ]
        partner_fields = [
            "record_id.vat",
            "record_id.property_product_pricelist",
            "record_id.property_account_position_id",
        ]
        return backend_fields + partner_address_fields + partner_fields

    @api.depends(lambda self: self._compute_sale_profile_id_depends())
    def _compute_sale_profile_id(self):
        """Compute sale_profile_id"""
        records = self.filtered("backend_id.use_sale_profile")
        for company in records.company_id:
            company_records = records.filtered(lambda rec: rec.company_id == company)
            company_records = company_records.with_company(company)
            for rec in company_records:
                rec.sale_profile_id = rec._get_sale_profile()
        # Records related to backends without use_sale_profile
        (self - records).sale_profile_id = False

    def _get_fiscal_position(self):
        """Get the partner's fiscal position"""
        self.ensure_one()
        return (
            self.env["account.fiscal.position"]
            .with_company(self.company_id)
            .get_fiscal_position(self.record_id.id)
        )

    def _get_sale_profile(self):
        """Get the sale profile that matches this partner

        For better performance, set the company on the recordset before
        calling this method, to avoid setting it record by record here.

        The best match is selected according to the following preference:

            1) profiles matching both fiscal_position_ids and pricelist_id
            2) profiles without pricelist_id matching fiscal_position_ids
            3) profiles without fiscal_position_ids matching pricelist_id
            4) profiles without fiscal_position_ids nor pricelist_id
            5) fallback to the backend's default sale profile
        """
        self.ensure_one()
        if self.env.company != self.company_id:
            self = self.with_company(self.company_id)

        fposition = self._get_fiscal_position()
        pricelist = self.property_product_pricelist
        profiles = self.backend_id.sale_profile_ids

        pricelist_empty = profiles.filtered(lambda p: not p.pricelist_id)
        pricelist_match = profiles.filtered(lambda p: pricelist == p.pricelist_id)
        fposition_empty = profiles.filtered(lambda p: not p.fiscal_position_ids)
        fposition_match = (
            profiles.filtered(lambda p: fposition in p.fiscal_position_ids)
            if fposition
            else profiles.browse()
        )

        matches = False

        # Case 1)
        if fposition_match and pricelist_match:
            matches = fposition_match & pricelist_match
        # Case 2)
        if not matches and fposition_match:
            matches = fposition_match & pricelist_empty
        # Case 3)
        if not matches and pricelist_match:
            matches = pricelist_match & fposition_empty
        # Case 4)
        if not matches:
            matches = pricelist_empty & fposition_empty
        # Case 5)
        if not matches:
            matches = self.backend_id._get_default_profile()
            if not matches:
                raise exceptions.UserError(
                    _(
                        "No default sale profile found for the backend %s",
                        self.backend_id.name,
                    )
                )

        return first(matches.sorted())
