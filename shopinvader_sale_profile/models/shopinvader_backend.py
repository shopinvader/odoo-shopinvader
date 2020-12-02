# Copyright 2018 Akretion (http://www.akretion.com).
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, exceptions, fields, models


class ShopinvaderBackend(models.Model):
    _inherit = "shopinvader.backend"

    use_sale_profile = fields.Boolean(
        default=False, help="Determine if this backend use sale profiles"
    )
    sale_profile_ids = fields.One2many(
        "shopinvader.sale.profile", "backend_id", "Customer sale profiles"
    )

    @api.onchange("use_sale_profile")
    def _onchange_use_sale_profile(self):
        if self.use_sale_profile:
            self.pricelist_id = False
        else:
            # TODO @simahawk: I don't get this...
            # If self.use_sale_profile is False
            # why shall you retrieve the pricelist from sale profiles?
            if self.sale_profile_ids and not self.pricelist_id:
                profile = (
                    self.sale_profile_ids.filtered("default")
                    or self.sale_profile_ids[0]
                )
                self.pricelist_id = profile.pricelist_id

    @api.constrains("use_sale_profile", "pricelist_id")
    def _check_use_sale_profile(self):
        # TODO: does this make sense?
        # We could set the pricelist in the onchange above
        if self.pricelist_id and self.use_sale_profile:
            raise exceptions.ValidationError(
                _(
                    "You can not use sale profile and set a specific "
                    "pricelist at the same time."
                )
            )

    def _get_cart_pricelist(self, partner=None):
        """Override to use default profile pricelist when needed.
        """
        pricelist = super()._get_cart_pricelist(partner)
        if not self.use_sale_profile:
            return pricelist
        profile_pricelist = self._get_profile_pricelist(partner)
        if profile_pricelist:
            return profile_pricelist
        return pricelist

    def _get_profile_pricelist(self, partner=None):
        default_profile_pricelist = self._get_default_profile_pricelist()
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
        return default_profile_pricelist

    def _get_default_profile_pricelist(self):
        # TODO: shall we override `_selection_default_role`
        # to list all profiles' code and pick the profile usin its code?
        profile = self.sale_profile_ids.filtered("default")
        if profile and profile.pricelist_id:
            return profile.pricelist_id
        return None
