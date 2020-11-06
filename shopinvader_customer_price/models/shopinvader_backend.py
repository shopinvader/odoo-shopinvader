# Copyright 2020 Camptocamp SA (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, tools


class ShopinvaderBackend(models.Model):

    _inherit = "shopinvader.backend"

    cart_pricelist_partner_field_id = fields.Many2one(
        comodel_name="ir.model.fields",
        domain=[
            ("model", "=", "res.partner"),
            ("ttype", "=", "many2one"),
            ("relation", "=", "product.pricelist"),
        ],
        help="Set the partner pricelist that will be used for the cart. "
        "WARNING: by changing this you might have a mismatch "
        "between the prices showed on the cart "
        "and the ones showed on product details. "
        "The default pricelist will still be used for products' indexes.",
    )

    @tools.ormcache("self.cart_pricelist_partner_field_id.id", "partner")
    def _get_cart_pricelist(self, partner=None):
        pricelist = super()._get_cart_pricelist(partner=partner)
        if self.cart_pricelist_partner_field_id and partner:
            pricelist = partner[self.cart_pricelist_partner_field_id.name]
        return pricelist

    @tools.ormcache("partner.id", "self.company_id.id")
    def _get_fiscal_position(self, partner):
        fp_model = self.env["account.fiscal.position"].with_context(
            force_company=self.company_id.id
        )
        fpos_id = fp_model.get_fiscal_position(
            partner.id, delivery_id=partner.id,
        )
        return fp_model.browse(fpos_id)
