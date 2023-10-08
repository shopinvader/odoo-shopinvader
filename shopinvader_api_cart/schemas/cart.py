# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from typing import List

from extendable_pydantic import StrictExtendableBaseModel


class CartTransaction(StrictExtendableBaseModel):
    uuid: str | None = None
    qty: float
    product_id: int


class CartSyncInput(StrictExtendableBaseModel):
    transactions: List[CartTransaction]
