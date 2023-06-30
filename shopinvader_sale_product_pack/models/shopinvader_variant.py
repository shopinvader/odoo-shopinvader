# Copyright 2023 ForgeFlow S.L. (http://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, models
from odoo.exceptions import ValidationError
from odoo.tools import float_is_zero, float_round


class ShopinvaderVariant(models.Model):
    _inherit = "shopinvader.variant"

    def _get_price(self, pricelist, fposition, company=None):
        self.ensure_one()
        if self.pack_ok:
            return self._get_product_pack_price(
                pricelist, fposition, company=company
            )
        else:
            return super()._get_price(pricelist, fposition, company=company)

    def _get_product_pack_price(self, pricelist, fposition, company=None):
        original_value = 0.0
        value = 0.0
        discount = 0.0
        for pack_line in self.sudo().pack_line_ids:
            shopinvader_variant_pack = self.search(
                [("record_id", "=", pack_line.product_id.id)]
            )
            if not shopinvader_variant_pack:
                raise ValidationError(
                    _("Product %s has no shopinvader variant configured")
                    % pack_line.product_id.name
                )
            pack_line_price = (
                shopinvader_variant_pack._get_price_per_qty(
                    pack_line.quantity, pricelist, fposition, company
                )["original_value"]
                * pack_line.quantity
            )
            original_value += pack_line_price
            value += pack_line_price * (1 - pack_line.sale_discount / 100)
        if not float_is_zero(original_value - value, precision_rounding=0.01):
            discount = (1 - value / original_value) * 100
            dicount_precision = self.env["decimal.precision"].precision_get(
                "Discount"
            )
            discount = float_round(discount, dicount_precision)
        return {
            "discount": discount,
            "original_value": original_value,
            "tax_included": False,
            "value": value,
        }
