# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    def _get_sale_pricelist(self):
        """
        By default use the pricelist set on the partner.
        But if a pricelist is set on the backend, use it.
        :return: product.pricelist recordset
        """
        self.ensure_one()
        pricelist = self.partner_id.property_product_pricelist
        if self.shopinvader_backend_id.pricelist_id:
            pricelist = self.shopinvader_backend_id.pricelist_id
        return pricelist

    def _update_pricelist_and_update_line_prices(self):
        """
        On current sale orders (self):
        - Update the pricelist with the one set on the backend;
            => If no pricelist, use the default define on the partner.
        - Then launch the price update (module sale_order_price_recalculation).
        :return: bool
        """
        pricelist_sales = {}
        for sale in self:
            pricelist = sale._get_sale_pricelist()
            sales = pricelist_sales.get(pricelist, self.browse())
            sales |= sale
            pricelist_sales.update({pricelist: sales})
        for pricelist, sales in pricelist_sales.items():
            sales.write({"pricelist_id": pricelist.id})
        # The date_der should be updated because some prices rules depends on the date.
        self.write({"date_order": fields.Datetime.now()})
        # Even if the pricelist is not updated on the SO, we have to launch
        # the price recalculation in case of pricelist content is updated.
        self.update_prices()
