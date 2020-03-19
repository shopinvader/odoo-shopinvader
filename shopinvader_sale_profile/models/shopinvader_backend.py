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
    def change_pricelist(self):
        if self.use_sale_profile:
            self.pricelist_id = False
        else:
            if self.sale_profile_ids and not self.pricelist_id:
                profile = (
                    self.sale_profile_ids.filtered("default")
                    or self.sale_profile_ids[0]
                )
                self.pricelist_id = profile.pricelist_id

    @api.multi
    @api.constrains("use_sale_profile", "pricelist_id")
    def _check_default(self):
        if self.pricelist_id and self.use_sale_profile:
            raise exceptions.ValidationError(
                _(
                    "You can not use sale profile and set a specific "
                    "pricelist at the same time."
                )
            )
