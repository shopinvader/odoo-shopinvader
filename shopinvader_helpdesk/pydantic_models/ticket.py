# Copyright 2022 Akretion (https://www.akretion.com).
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from typing import List

from pydantic import BaseModel, Field

from odoo.addons.base_rest_pydantic.pydantic_models.base import IdAndNameInfo, IdRequest
from odoo.addons.helpdesk_mgmt_rest_api.pydantic_models.ticket import (
    HelpdeskTicketInfo,
    HelpdeskTicketRequest,
)
from odoo.addons.pydantic import utils


class HelpdeskTicketSaleLineRequest(BaseModel):
    sale_line_id: int
    qty: int = None


class HelpdeskTicketSaleLineInfo(BaseModel):
    sale_line_id: int
    qty: int
    product_name: str = None

    class Config:
        orm_mode = True
        getter_dict = utils.GenericOdooGetter


class HelpdeskTicketRequest(HelpdeskTicketRequest):
    sale: IdRequest = Field(None, alias="sale_id")


class HelpdeskTicketInfo(HelpdeskTicketInfo):
    sale: IdAndNameInfo = Field(None, alias="sale_id")
    sale_lines: List[HelpdeskTicketSaleLineInfo] = Field([], alias="sale_line_ids")
