# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.addons.component.core import AbstractComponent


class AbstractSaleService(AbstractComponent):
    _inherit = "shopinvader.abstract.sale.service"

    def _convert_one_sale(self, sale):
        """
        Inherit to add the picking note into the result
        :param sale: sale.order recordset
        :return: dict
        """
        values = super()._convert_one_sale(sale)
        values.update({"delivery_instruction": sale.picking_note})
        return values
