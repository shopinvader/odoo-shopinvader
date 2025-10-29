# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from extendable_pydantic import StrictExtendableBaseModel


class ImageData(StrictExtendableBaseModel):
    sequence: int = 0
    src: str
    alt: str = ""
    tag: str = ""

    @classmethod
    def from_image_relation_mixin(
        cls, record, image_relation, sequence, backend, thumbnail
    ):
        tag = ""
        if "tag_id" in image_relation._fields:
            tag = image_relation.tag_id.name or ""
        if "sequence" in image_relation._fields:
            sequence = image_relation.sequence

        return cls.model_construct(
            sequence=sequence,
            src=backend._get_image_url_for_image(thumbnail.image),
            alt=record.name,
            tag=tag,
        )
