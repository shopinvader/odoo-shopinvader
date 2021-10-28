# Copyright 2021 Camptocamp SA
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import AbstractComponent


class AbstractSaleService(AbstractComponent):
    _inherit = "shopinvader.abstract.sale.service"

    def _convert_one_line(self, line):
        res = super()._convert_one_line(line)
        res.update({"options": self._convert_options(line.option_ids)})
        return res

    def _convert_options(self, options):
        return [self._convert_one_option(option) for option in options]

    def _convert_one_option(self, option):
        option.ensure_one()
        return {
            "id": option.id,
            "qty_type": option.option_qty_type,
            "unit_qty": option.option_unit_qty,
        }
