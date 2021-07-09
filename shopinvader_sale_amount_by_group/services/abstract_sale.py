# Copyright 2021 Camptocamp SA
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import AbstractComponent


class AbstractSaleService(AbstractComponent):
    _inherit = "shopinvader.abstract.sale.service"

    def _convert_amount(self, sale):
        res = super()._convert_amount(sale)
        res["amount_by_group"] = [
            {
                "name": name,
                "amount": amount,
                "base": base,
            }
            for name, amount, base, *__ in sale.amount_by_group
        ]
        return res
