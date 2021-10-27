# Copyright 2018 Akretion (http://www.akretion.com).
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# @author Simone Orsi <simahawk@gmail.com>
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, exceptions, fields, models


class ShopinvaderBackend(models.Model):
    _inherit = "shopinvader.backend"

    pricelist_id = fields.Many2one(
        compute="_compute_pricelist_id",
        store=True,
        readonly=False,
    )
    use_sale_profile = fields.Boolean(
        default=False, help="Determine if this backend use sale profiles"
    )
    sale_profile_ids = fields.One2many(
        "shopinvader.sale.profile", "backend_id", "Customer sale profiles"
    )

    @api.depends("use_sale_profile", "sale_profile_ids.default")
    def _compute_pricelist_id(self):
        for rec in self:
            if rec.use_sale_profile:
                rec.pricelist_id = rec._get_default_profile().pricelist_id
            else:
                rec.pricelist_id = rec._default_pricelist_id()

    def _compute_customer_default_role(self):
        # Override. Get default role from default profile
        # If the backend doesn't use_sale_profile, fallback to super()
        using_sale_profile = self.filtered("use_sale_profile")
        for rec in using_sale_profile:
            rec.customer_default_role = rec._get_default_profile().code
        other_records = self - using_sale_profile
        super(ShopinvaderBackend, other_records)._compute_customer_default_role()

    @api.constrains("use_sale_profile", "pricelist_id")
    def _check_use_sale_profile(self):
        if any(rec.use_sale_profile and not rec.pricelist_id for rec in self):
            raise exceptions.ValidationError(
                _("You must have a default profile that provides a default pricelist.")
            )

    def _get_partner_pricelist(self, partner):
        pricelist = super()._get_partner_pricelist(partner)
        if not self.use_sale_profile:
            return pricelist
        profile_pricelist = self._get_profile_pricelist(partner)
        if profile_pricelist:
            return profile_pricelist
        return pricelist

    def _get_profile_pricelist(self, partner=None):
        default_profile = self._get_default_profile()
        # TODO: we should receive shopinvader.partner all around
        invader_partner = (
            partner._get_invader_partner(self)
            if partner
            else self.env["shopinvader.partner"].browse()
        )
        if invader_partner and invader_partner.sale_profile_id:
            # If the partner has been created via shopinvader this will match
            # property_product_pricelist already
            return invader_partner.sale_profile_id.pricelist_id
        return default_profile.pricelist_id

    def _get_default_profile(self):
        return self.sale_profile_ids.filtered("default")
