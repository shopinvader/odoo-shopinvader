# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from extendable_pydantic import StrictExtendableBaseModel


class MediaType(StrictExtendableBaseModel):
    name: str
    code: str | None = None

    @classmethod
    def from_media_type(cls, odoo_rec):
        return cls.model_construct(
            name=odoo_rec.name,
            code=odoo_rec.code or None,
        )
