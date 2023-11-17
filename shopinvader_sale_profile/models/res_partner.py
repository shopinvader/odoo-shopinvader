# Copyright 2018 Akretion (http://www.akretion.com).
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# Copyright 2021 Camptocamp SA (https://www.camptocamp.com)
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = "res.partner"

    sale_profile_id = fields.Many2one(
        "shopinvader.sale.profile",
        "Sale profile",
        compute="_compute_sale_profile_id",
        help="Sale profile computed, depending every fields who make the "
        "fiscal position (country, zip, vat, account position,...)",
    )

    @api.model
    def _compute_sale_profile_id_depends(self):
        # Using `_address_fields` gives us a lazy compatibility
        # with modules like `base_address_city` or `base_location`
        partner_address_fields = [
            f"{fname}"
            for fname in self.env["res.partner"]._address_fields()
            if not fname.startswith("street")
        ]
        partner_fields = [
            "vat",
            "property_product_pricelist",
            "property_account_position_id",
        ]
        return partner_address_fields + partner_fields

    @api.depends(lambda self: self._compute_sale_profile_id_depends())
    def _compute_sale_profile_id(self):
        """Compute sale_profile_id"""
        for partner in self:
            partner.sale_profile_id = partner._get_sale_profile(
                self.env["shopinvader.sale.profile"].search([])
            )

    def _get_fiscal_position(self):
        """Get the partner's fiscal position"""
        self.ensure_one()
        return (
            self.env["account.fiscal.position"]
            .with_company(self.company_id)
            ._get_fiscal_position(self)
        )

    def _get_sale_profile(self, sale_profiles, default=None):
        """Get the sale profile that matches this partner

        The best match is selected according to the following preference:

            1) profiles matching both fiscal_position_ids and pricelist_id
            2) profiles without pricelist_id matching fiscal_position_ids
            3) profiles without fiscal_position_ids matching pricelist_id
            4) profiles without fiscal_position_ids nor pricelist_id
            5) fallback to the default sale profile
        """
        self.ensure_one()
        fposition = self._get_fiscal_position()
        pricelist = self.property_product_pricelist

        pricelist_empty = sale_profiles.filtered(lambda p: not p.pricelist_id)
        pricelist_match = sale_profiles.filtered(lambda p: pricelist == p.pricelist_id)
        fposition_empty = sale_profiles.filtered(lambda p: not p.fiscal_position_ids)
        fposition_match = (
            sale_profiles.filtered(lambda p: fposition in p.fiscal_position_ids)
            if fposition
            else sale_profiles.browse()
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
            matches = default
            if not matches:
                raise UserError(_("No default sale profile found"))

        return fields.first(matches.sorted())
