# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    def _update_pricelist_and_update_line_prices(self):
        """
        On current sale orders (self):
        - Update the pricelist with the one set on the backend;
            => If no pricelist, use the default define on the partner.
        - Then launch the price update (module sale_order_price_recalculation).
        :return: bool
        """
        backends = self.mapped("shopinvader_backend_id").filtered(
            lambda b: b.pricelist_id
        )
        other_sales = self
        for backend in backends:
            pricelist = backend.pricelist_id
            sales = self.filtered(lambda s, b=backend: s.shopinvader_backend_id == b)
            other_sales -= sales
            sales.write({"pricelist_id": pricelist.id})
        # We don't have a pricelist on the backend so use the one set
        # on the partner
        partner_pricelists = other_sales.mapped("partner_id.property_product_pricelist")
        # Group by pricelist to do less write as possible.
        for pricelist in partner_pricelists:
            sales = other_sales.filtered(
                lambda s, p=pricelist: s.partner_id.property_product_pricelist == p
            )
            sales.write({"pricelist_id": pricelist.id})
        # The date_der should be updated because some prices rules depends on the date.
        self.write({"date_order": fields.Datetime.now()})
        # Even if the pricelist is not updated on the SO, we have to launch
        # the price recalculation in case of pricelist content is updated.
        # TODO: Adapt to v13 sale-workflow/sale_order_price_recalculation could be used
        # self.update_prices()

