# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.extendable_fastapi.schemas import StrictExtendableBaseModel

from . import MediaType


class MediaData(StrictExtendableBaseModel):
    sequence: int | None = None
    name: str
    url: str
    media_type: MediaType | None = None

    @classmethod
    def from_media_data(cls, odoo_rec):
        return cls.model_construct(
            sequence=odoo_rec.sequence or None,
            name=odoo_rec.name,
            url=odoo_rec.read(["fs_file"])[0]["fs_file"]["url"],
            media_type=MediaType.from_media_type(odoo_rec.media_type_id)
            if odoo_rec.media_type_id
            else None,
        )
