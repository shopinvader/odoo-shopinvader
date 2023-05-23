# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.tools import float_compare, float_is_zero, float_round

from odoo.addons.component.core import Component


class CustomerPriceService(Component):
    _inherit = "shopinvader.customer.price.service"

    def _to_json(self, records, **kw):
        pricelist = self.shopinvader_backend._get_cart_pricelist(self.partner)
        if pricelist.is_pricelist_cache_available:
            return self._get_cached_prices(records)
        # Falling back to the original implementation when pricelist cache
        # is inconsistent (once a day)
        return super()._to_json(records, **kw)

    def _get_cached_prices(self, records):
        pricelist = self.shopinvader_backend._get_cart_pricelist(self.partner)
        company = self.shopinvader_backend.company_id
        products = records.record_id
        price_caches = self.env[
            "product.pricelist.cache"
        ].get_cached_prices_for_pricelist(pricelist, products)
        AccountTax = self.env["account.tax"]
        price_dp = self.env["decimal.precision"].precision_get("Product Price")
        res = []
        for cache in price_caches:
            # TODO extract this in a dedicated method in order to avoid duplicated code.
            # This piece of code is copied from `shopinvader_variant::_get_price`.
            # It applies the right taxes on prices, and computes the discount.
            product = cache.product_id
            taxes = product.taxes_id.filtered(lambda tax: tax.company_id == company)
            price_unit = cache.price
            price_unit = AccountTax._fix_tax_included_price_company(
                price_unit, product.taxes_id, taxes, company
            )
            original_price_unit = product.price
            original_price_unit = AccountTax._fix_tax_included_price_company(
                original_price_unit, product.taxes_id, taxes, company
            )
            price_is_zero = float_is_zero(
                original_price_unit, precision_digits=price_dp
            )
            is_discounted = float_compare(
                original_price_unit, price_unit, precision_digits=price_dp
            )
            if not price_is_zero and is_discounted:
                discount = (
                    (original_price_unit - price_unit) / original_price_unit * 100
                )
                # Apply the right precision on discount
                discount_dp = self.env["decimal.precision"].precision_get("Discount")
                discount = float_round(discount, discount_dp)
            else:
                discount = 0.00
            res.append(
                {
                    "id": product.id,
                    "price": {
                        self.invader_partner.role: {
                            "value": price_unit,
                            "original_value": original_price_unit,
                            "tax_included": any(tax.price_include for tax in taxes),
                            "discount": discount,
                        },
                    },
                }
            )
        return res
