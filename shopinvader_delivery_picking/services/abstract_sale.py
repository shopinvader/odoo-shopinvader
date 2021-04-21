# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo.addons.component.core import AbstractComponent

_logger = logging.getLogger(__name__)


class AbstractSaleService(AbstractComponent):
    _inherit = "shopinvader.abstract.sale.service"

    def _convert_one_sale(self, sale):
        res = super()._convert_one_sale(sale)
        res["picking_policy"] = sale.picking_policy
        res["commitment_date"] = sale.commitment_date
        res["expected_date"] = sale.expected_date
        return res
