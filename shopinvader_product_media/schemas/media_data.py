# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.extendable_fastapi.schemas import StrictExtendableBaseModel

from . import MediaType


class MediaData(StrictExtendableBaseModel):
    sequence: int | None = None
    name: str
    url: str
    type: MediaType | None = None

    @classmethod
    def from_media_data(cls, odoo_rec):
        index = odoo_rec.env["se.index"].browse(odoo_rec.env.context["index_id"])
        backend = index.backend_id
        return cls.model_construct(
            sequence=odoo_rec.sequence or None,
            name=odoo_rec.name,
            url=backend._get_url_for_media(odoo_rec.file),
            type=MediaType.from_media_type(odoo_rec.media_type_id)
            if odoo_rec.media_type_id
            else None,
        )
