# Copyright 2022 Akretion (https://www.akretion.com).
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import AbstractComponent


class AbstractSaleService(AbstractComponent):
    _name = "shopinvader.abstract.sale.service"
    _inherit = ["shopinvader.abstract.sale.service", "abstract.attachable.service"]

    def _convert_one_sale(self, sale):
        res = super()._convert_one_sale(sale)
        res["attachments"] = self._json_parser_attachments()
        return res
