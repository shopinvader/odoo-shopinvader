# Copyright 2017 Akretion (http://www.akretion.com)
# @author Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.addons.component.core import AbstractComponent


class AbstractSaleService(AbstractComponent):
    _inherit = "shopinvader.abstract.sale.service"

    def _is_item(self, line):
        res = super()._is_item(line)
        return res and not line.is_promotion_line
