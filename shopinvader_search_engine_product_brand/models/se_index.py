# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from ..tools.brand_serializer import ProductBrandShopinvaderSerializer


class SeIndex(models.Model):

    _inherit = "se.index"

    serializer_type = fields.Selection(
        selection_add=[
            ("shopinvader_brand_exports", "Shopinvader Product Brand"),
        ],
        ondelete={
            "shopinvader_brand_exports": "cascade",
        },
    )

    @api.constrains("model_id", "serializer_type")
    def _check_model(self):
        brand_model = self.env["ir.model"].search(
            [("model", "=", "product.brand")], limit=1
        )
        for se_index in self:
            if (
                se_index.serializer_type == "shopinvader_brand_exports"
                and se_index.model_id != brand_model
            ):
                raise ValidationError(_("'Serializer Type' must match 'Model'"))

    def _get_serializer(self):
        self.ensure_one()
        if self.serializer_type == "shopinvader_brand_exports":
            return ProductBrandShopinvaderSerializer()
        else:
            return super()._get_serializer()
