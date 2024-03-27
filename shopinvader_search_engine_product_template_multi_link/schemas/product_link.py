# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from typing import Annotated

from extendable_pydantic import StrictExtendableBaseModel
from pydantic import Field


class ProductLink(StrictExtendableBaseModel):
    """Information related to a product linked to the current product"""

    id: Annotated[int, Field(description="The id of the product")]

    @classmethod
    def from_product_product(cls, product):
        return cls.model_construct(
            id=product.id,
        )
