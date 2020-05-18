# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import AbstractComponent


class AbstractSaleService(AbstractComponent):
    _inherit = "shopinvader.abstract.sale.service"

    def _convert_one_sale(self, sale):
        values = super(AbstractSaleService, self)._convert_one_sale(sale)
        values.update(
            {
                "online_information_for_customer": sale.online_information_for_customer,
                "online_information_request": sale.online_information_request,
            }
        )
        return values
