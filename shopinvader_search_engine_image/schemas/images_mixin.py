# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from extendable_pydantic import StrictExtendableBaseModel
from pydantic import fields

from odoo.exceptions import UserError

from odoo.addons.search_engine_image_thumbnail.models.se_indexable_record import (
    SeIndexableRecord,
)

from ..models.se_backend import SeBackend
from .image_data import ImageData


class ImageMixin(StrictExtendableBaseModel):
    images: list[dict[str, ImageData]] = fields.Field(
        default_factory=list,
        description="A list of dictionary of image data by image size code."
        "The order of the list is the order of the images in the original Odoo "
        "record. ",
        # fmt: off
        # flake8: noqa
        examples=[
            [
                {
                    "small": {
                        "sequence": 0,
                        "src": "https://media.alcyonbelux.be/media/"
                                "table-nac-inox-60-60-222886.jpg",
                        "alt": "TABLE NAC INOX",
                        "tag": "",
                    },
                    "large": {
                        "sequence": 0,
                        "src": "https://media.alcyonbelux.be/media/"
                                "table-nac-inox-550-550-222888.jpg",
                        "alt": "TABLE NAC INOX",
                        "tag": "",
                    },
                    "medium": {
                        "sequence": 0,
                        "src": "https://media.alcyonbelux.be/media/"
                               "table-nac-inox-300-300-222887.jpg",
                        "alt": "TABLE NAC INOX",
                        "tag": "",
                    },
                }
            ]
        ],
        # fmt: on
    )

    def _fill_image_from_image_relation_mixin(
        self, record: SeIndexableRecord, field_name: str
    ):
        """Fill the images field from a FsImageRelationMixin field."""
        index = record.env["se.index"].browse(record.env.context["index_id"])
        backend: SeBackend = index.backend_id
        self.images = []
        try:
            size_and_thumbnails_by_image = (
                record._get_or_create_thumbnails_for_multi_images(
                    index=index, field_name=field_name
                )
            )
        except UserError:
            # No thumbnail sizes defined on backend
            return
        cpt = 0
        for (
            image_relation,
            size_and_thumbnails,
        ) in size_and_thumbnails_by_image.items():
            thumbs = {}
            for size, thumbnail in size_and_thumbnails:
                tag = ""
                if "tag_id" in image_relation._fields:
                    tag = image_relation.tag_id.name or ""
                sequence = cpt
                if "sequence" in image_relation._fields:
                    sequence = image_relation.sequence
                thumbs[size.key] = ImageData(
                    sequence=sequence,
                    src=backend._get_image_url_for_image(thumbnail.image),
                    alt=record.name,
                    tag=tag,
                )
            if thumbs:
                self.images.append(thumbs)
            cpt += 1
