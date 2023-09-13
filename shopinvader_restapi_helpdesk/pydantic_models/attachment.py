# Copyright 2022 Akretion (https://www.akretion.com).
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from typing import List

from pydantic import BaseModel, Field

from .base import IdAndNameInfo


class AttachmentRequest(BaseModel):
    name: str = None


class AttachmentInfo(BaseModel):
    id: int
    name: str

    @classmethod
    def from_rec(cls, odoo_rec):
        return cls.model_construct(
            id=odoo_rec.id,
            name=odoo_rec.name,
        )


class AttachableInfo(BaseModel):
    attachments: List[IdAndNameInfo] = Field([], alias="attachment_ids")

    @classmethod
    def from_rec(cls, odoo_rec):
        return cls.model_construct(
            attachments=[IdAndNameInfo.from_rec(rec) for rec in odoo_rec.attachment_ids]
        )
