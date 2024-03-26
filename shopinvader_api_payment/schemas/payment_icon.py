# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from extendable_pydantic import StrictExtendableBaseModel
from pydantic import Base64Bytes


class PaymentIcon(StrictExtendableBaseModel):
    name: str | None
    sequence: int | None
    image: Base64Bytes | None

    @classmethod
    def from_payment_icon(cls, odoo_rec):
        return cls.model_construct(
            name=odoo_rec.name or None,
            sequence=odoo_rec.sequence or None,
            image=odoo_rec.image or None,
        )
