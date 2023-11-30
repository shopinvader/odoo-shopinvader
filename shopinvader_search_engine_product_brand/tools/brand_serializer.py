# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.addons.search_engine_serializer_pydantic.tools.serializer import (
    PydanticModelSerializer,
)
from odoo.addons.shopinvader_product_brand.schemas import ProductBrand


class ProductBrandShopinvaderSerializer(PydanticModelSerializer):
    def get_model_class(self):
        return ProductBrand

    def serialize(self, record):
        return self.get_model_class().from_product_brand(record).model_dump(mode="json")
