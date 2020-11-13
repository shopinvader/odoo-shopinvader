# Copyright 2018 Akretion (http://www.akretion.com).
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# @author Sébastien BEAU <sebastien.beau@akretion.com>
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
        if self.pricelist_id and self.use_sale_profile:
            raise exceptions.ValidationError(
                _(
                    "You can not use sale profile and set a specific "
                    "pricelist at the same time."
                )
            )

    def _get_customer_default_pricelist(self):
        """Override to use default profile pricelist when needed.
        """
        pricelist = super()._get_customer_default_pricelist()
        if self.use_sale_profile:
            # TODO: shall we override `_selection_default_role`
            # to list all profiles' code and pick the profile usin its code?
            profile = self.sale_profile_ids.filtered("default")
            if profile and profile.pricelist_id:
                pricelist = profile.pricelist_id
        return pricelist
