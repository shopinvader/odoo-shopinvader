# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from typing import List

from fastapi import APIRouter

from odoo import api, fields, models


class FastapiEndpoint(models.Model):

    _inherit = "fastapi.endpoint"

    app: str = fields.Selection(
        selection_add=[("shopinvader_demo", "Shopinvader Demo Endpoint")],
        ondelete={"shopinvader_demo": "cascade"},
    )

    @api.model
    def _get_fastapi_routers(self):
        if self.app == "shopinvader_demo":
            return self._get_shopinvader_demo_fastapi_routers()
        return super().get_fastapi_routers()

    @api.model
    def _get_shopinvader_demo_fastapi_routers(self) -> List[APIRouter]:
        return []
