# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from ..routers.address_service import address_router


class FastapiEndpoint(models.Model):

    _inherit = "fastapi.endpoint"

    app: str = fields.Selection(
        selection_add=[("address", "Address Endpoint")], ondelete={"address": "cascade"}
    )

    @api.model
    def _get_fastapi_routers(self):
        if self.app == "address":
            return [address_router]
        return super()._get_fastapi_routers()
