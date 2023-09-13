# Copyright 2022 Akretion (https://www.akretion.com).
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from datetime import datetime
from typing import List

from pydantic import BaseModel, Field

from odoo import fields

from .base import IdAndNameInfo, IdRequest


class MailMessageBase(BaseModel):
    body: str


class MailMessageRequest(MailMessageBase):
    attachments: List[IdRequest] = Field([])


class MailMessageInfo(MailMessageBase):
    id: int
    date: datetime
    author: IdAndNameInfo = Field(None, alias="author_id")

    @classmethod
    def from_rec(cls, odoo_rec):
        return cls.model_construct(
            id=odoo_rec.id,
            date=fields.Datetime.context_timestamp(odoo_rec, odoo_rec.date)
            if odoo_rec.date
            else None,
            body=odoo_rec.body,
            author=IdAndNameInfo.from_rec(odoo_rec.author_id),
        )


class MailThreadInfo(BaseModel):
    messages: List[MailMessageInfo] = Field([], alias="message_ids")
