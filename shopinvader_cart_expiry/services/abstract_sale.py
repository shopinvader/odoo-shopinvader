# Copyright 2019 ACSONE SA/NV https://acsone.eu
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.component.core import AbstractComponent


class AbstractSaleService(AbstractComponent):

    _inherit = "shopinvader.abstract.sale.service"

    def _convert_one_sale(self, sale):
        res = super(AbstractSaleService, self)._convert_one_sale(sale)
        res.update({"expiration_date": sale.cart_expiration_date})
        return res
