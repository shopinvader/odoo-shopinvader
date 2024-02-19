# Copyright 2018 Akretion (http://www.akretion.com).
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ShopinvaderSaleProfile(models.Model):
    _name = "shopinvader.sale.profile"
    _description = "Shopinvader Customer profile"
    _rec_name = "code"

    pricelist_id = fields.Many2one(
        "product.pricelist", "Pricelist", help="Pricelist used for the sale profile"
    )
    fiscal_position_ids = fields.Many2many(
        "account.fiscal.position",
        "shopinvader_sale_profile_fiscal_position_rel",
        "shopinvader_sale_profile",
        "fiscal_position_id",
        help="This sale profile is applied for these fiscal positions",
    )
    code = fields.Char(
        required=True, help="Unique code of the sale profile", index=True
    )
