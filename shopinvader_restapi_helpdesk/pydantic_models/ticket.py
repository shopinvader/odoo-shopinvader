# Copyright 2022 Akretion (https://www.akretion.com).
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from odoo import fields

from .attachment import AttachableInfo
from .base import IdAndNameInfo, IdRequest
from .mail_message import MailThreadInfo


class HelpdeskPartnerRequest(BaseModel):
    email: EmailStr
    name: str
    lang: str = None


class HelpdeskTicketSaleLineRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    sale_line_id: int
    qty: int = None


class HelpdeskTicketSaleLineInfo(BaseModel):
    sale_line_id: int
    qty: int
    product_name: str = None

    @classmethod
    def from_rec(cls, sol):
        return cls.model_construct(
            sale_line_id=sol.id, qty=sol.qty, product_name=sol.product_name
        )


class HelpdeskTicketInfo(AttachableInfo, MailThreadInfo):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str
    create_date: datetime
    last_stage_update: datetime
    category: IdAndNameInfo = Field(None, alias="category_id")
    team: IdAndNameInfo = Field(None, alias="team_id")
    stage: IdAndNameInfo = Field(None, alias="stage_id")

    sale: IdAndNameInfo = Field(None, alias="sale_id")
    sale_lines: List[HelpdeskTicketSaleLineInfo] = Field([], alias="sale_line_ids")

    @classmethod
    def from_rec(cls, odoo_rec):
        return cls.model_construct(
            id=odoo_rec.id,
            name=odoo_rec.name or None,
            description=odoo_rec.description or None,
            create_date=fields.Datetime.context_timestamp(
                odoo_rec, odoo_rec.create_date
            )
            if odoo_rec.create_date
            else None,
            last_stage_update=fields.Datetime.context_timestamp(
                odoo_rec, odoo_rec.last_stage_update
            )
            if odoo_rec.last_stage_update
            else None,
            category=IdAndNameInfo.from_rec(odoo_rec.category_id),
            team=IdAndNameInfo.from_rec(odoo_rec.team_id),
            stage=IdAndNameInfo.from_rec(odoo_rec.stage_id),
            sale=IdAndNameInfo.from_rec(odoo_rec.sale_id),
            sale_lines=[
                HelpdeskTicketSaleLineInfo.from_rec(sol)
                for sol in odoo_rec.sale_line_ids
            ],
        )


class HelpdeskTicketRequest(BaseModel):
    name: str
    description: str
    partner: HelpdeskPartnerRequest = Field(None)
    category: IdRequest = Field(None)
    team: IdRequest = Field(None)
    sale: IdRequest = Field(None, alias="sale_id")
