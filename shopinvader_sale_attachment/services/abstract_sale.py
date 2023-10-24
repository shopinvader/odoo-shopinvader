# Copyright 2022 Akretion (https://www.akretion.com).
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _
from odoo.exceptions import MissingError

from odoo.addons.component.core import AbstractComponent


class AbstractSaleService(AbstractComponent):
    _name = "shopinvader.abstract.sale.service"
    _inherit = ["abstract.attachable.service", "shopinvader.abstract.sale.service"]

    def _convert_one_sale(self, sale):
        res = super()._convert_one_sale(sale)
        items = []
        attachments = self.env["ir.attachment"].search(
            [("res_id", "=", sale.id), ("res_model", "=", "sale.order")]
        )
        for attachment in attachments:
            items.append({"id": attachment.id, "name": attachment.name})
        res["attachments"] = items
        return res

    def _check_attachment_access(self, record):
        if not self._get(record.id):
            raise MissingError(
                _("There is no attachment for this record: {}".format(record.id))
            )
