# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.search_engine_serializer_pydantic.tools.serializer import (
    PydanticModelSerializer,
)
from odoo.addons.shopinvader_product.schemas.category import ProductCategory


class ProductCategoryShopinvaderSerializer(PydanticModelSerializer):
    def get_model_class(self):
        return ProductCategory

    def serialize(self, record):
        return self.get_model_class().from_product_category(record).model_dump()
