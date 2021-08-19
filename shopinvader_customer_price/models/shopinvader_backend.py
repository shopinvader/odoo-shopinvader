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

    @tools.ormcache("partner.id", "self.cart_pricelist_partner_field_id.id")
    def _get_cart_pricelist_id(self, partner):
        if self.cart_pricelist_partner_field_id:
            pricelist = partner[self.cart_pricelist_partner_field_id.name]
            return pricelist.id
        return None

    def _get_cart_pricelist(self, partner=None):
        pricelist = super()._get_cart_pricelist(partner)
        if partner:
            pricelist_id = self._get_cart_pricelist_id(partner)
            if pricelist_id:
                return self.env["product.pricelist"].browse(pricelist_id)
        return pricelist

    def _get_partner_pricelist(self, partner):
        pricelist = super()._get_partner_pricelist(partner)
        if pricelist is None:
            pricelist = partner.property_product_pricelist
        return pricelist

    @tools.ormcache("partner.id", "self.company_id.id")
    def _get_fiscal_position_id(self, partner):
        fp_model = self.env["account.fiscal.position"].with_company(self.company_id.id)
        fpos = fp_model.get_fiscal_position(
            partner.id,
            delivery_id=partner.id,
        )
        return fpos.id

    def _get_fiscal_position(self, partner):
        fpos_id = self._get_fiscal_position_id(partner)
        return (
            self.env["account.fiscal.position"].browse(fpos_id)
            if fpos_id
            else self.env["account.fiscal.position"].browse()
        )
