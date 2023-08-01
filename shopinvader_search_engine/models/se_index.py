# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from ..tools.category_serializer import ProductCategoryShopinvaderSerializer
from ..tools.product_serializer import ProductProductShopinvaderSerializer


class SeIndex(models.Model):

    _inherit = "se.index"

    serializer_type = fields.Selection(
        selection_add=[
            ("shopinvader_category_exports", "Shopinvader Category"),
            ("shopinvader_product_exports", "Shopinvader Product"),
        ],
        ondelete={
            "shopinvader_category_exports": "cascade",
            "shopinvader_product_exports": "cascade",
        },
    )

    @api.constrains("model_id", "serializer_type")
    def _check_model(self):
        category_model = self.env["ir.model"].search(
            [("model", "=", "product.category")], limit=1
        )
        product_model = self.env["ir.model"].search(
            [("model", "=", "product.product")], limit=1
        )
        for se_index in self:
            if (
                se_index.serializer_type == "shopinvader_category_exports"
                and se_index.model_id != category_model
            ) or (
                se_index.serializer_type == "shopinvader_product_exports"
                and se_index.model_id != product_model
            ):
                raise ValidationError(_("'Serializer Type' must match 'Model'"))

    def _get_serializer(self):
        self.ensure_one()
        if self.serializer_type == "shopinvader_category_exports":
            return ProductCategoryShopinvaderSerializer()
        elif self.serializer_type == "shopinvader_product_exports":
            return ProductProductShopinvaderSerializer()
        else:
            return super()._get_serializer()
