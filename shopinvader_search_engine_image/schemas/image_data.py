# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from extendable_pydantic import StrictExtendableBaseModel


class ImageData(StrictExtendableBaseModel):
    sequence: int = 0
    src: str
    alt: str = ""
    tag: str = ""
