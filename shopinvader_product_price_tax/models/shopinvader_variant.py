# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ShopinvaderVariant(models.Model):
    _inherit = "shopinvader.variant"

    def _get_price(
        self, qty=1.0, pricelist=None, fposition=None, company=None, date=None
    ):
        res = super()._get_price(
            qty=qty,
            pricelist=pricelist,
            fposition=fposition,
            company=company,
            date=date,
        )
        # Apply company
        product = self.record_id
        product = product.with_company(company) if company else product
        company = company or self.env.company
        # Always filter taxes by the company
        taxes = product.taxes_id.filtered(lambda tax: tax.company_id == company)
        # Apply fiscal position
        taxes = fposition.map_tax(taxes, product) if fposition else taxes
        # Compute tax amounts
        prices = taxes.compute_all(
            res["value"],
            product=product,
            quantity=1.0,  # only use quantity for pricelist rules, not here
            currency=pricelist.currency_id if pricelist else None,
        )
        res.update(
            {
                "value_untaxed": prices["total_excluded"],
                "value_taxed": prices["total_included"],
                "original_value_untaxed": prices["total_excluded"],
                "original_value_taxed": prices["total_included"],
            }
        )
        # Handle pricelists.discount_policy == "without_discount"
        if pricelist and pricelist.discount_policy == "without_discount":
            # Compute tax amounts
            prices = taxes.compute_all(
                res["original_value"],
                product=product,
                quantity=1.0,  # only use quantity for pricelist rules, not here
                currency=pricelist.currency_id if pricelist else None,
            )
            res.update(
                {
                    "original_value_untaxed": prices["total_excluded"],
                    "original_value_taxed": prices["total_included"],
                }
            )
        return res
