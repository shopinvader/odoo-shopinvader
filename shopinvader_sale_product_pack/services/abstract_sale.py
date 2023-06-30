# Copyright 2023 ForgeFlow S.L. (http://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.addons.component.core import AbstractComponent


class AbstractSaleService(AbstractComponent):
    _inherit = "shopinvader.abstract.sale.service"

    def _convert_one_line(self, line):
        res = super()._convert_one_line(line)
        if line.pack_parent_line_id or line.pack_child_line_ids:
            res.update(
                {
                    "pack_modifiable": line.pack_modifiable,
                    "pack_parent_line_id": line.pack_parent_line_id.id,
                    "pack_type": line.pack_type,
                    "pack_component_price": line.pack_component_price,
                    "pack_depth": line.pack_depth,
                }
            )
        return res
