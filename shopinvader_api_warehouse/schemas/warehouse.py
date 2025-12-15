# Copyright 2025 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from typing import Annotated

from extendable_pydantic import StrictExtendableBaseModel
from pydantic import Field

from odoo import api


class Warehouse(StrictExtendableBaseModel):
    id: int
    name: str | None = None
    code: str | None = None
    default: bool | None = None
    address: str | None = None
    city: str | None = None
    zip: str | None = None
    country: str | None = None
    phone: str | None = None
    email: str | None = None

    @classmethod
    def from_stock_warehouse(cls, odoo_rec, partner=None):
        address = odoo_rec.sudo().partner_id
        country_name = address.country_id.name if address.country_id else None
        return cls.model_construct(
            id=odoo_rec.id,
            name=odoo_rec.name or None,
            code=odoo_rec.code or None,
            default=partner.shopinvader_default_warehouse_id == odoo_rec
            if partner and partner.shopinvader_default_warehouse_id
            else None,
            address=address.street or None,
            city=address.city or None,
            zip=address.zip or None,
            country=country_name,
            phone=address.phone or None,
            email=address.email or None,
        )


class WarehouseSearch(StrictExtendableBaseModel, extra="ignore"):
    name: Annotated[
        str | None,
        Field(
            description="When used, the search look for any warehouse where name "
            "contains the given value case insensitively."
        ),
    ] = None
    code: Annotated[
        str | None,
        Field(
            description="When used, the search look for any warehouse where code "
            "contains the given value case insensitively."
        ),
    ] = None
    city: Annotated[
        str | None,
        Field(
            description="When used, the search look for any warehouse where city "
            "contains the given value case insensitively."
        ),
    ] = None
    country: Annotated[
        str | None,
        Field(
            description="When used, the search look for any warehouse where country "
            "contains the given value case insensitively."
        ),
    ] = None

    def to_odoo_domain(self, env: api.Environment):
        domain = []
        if self.name:
            domain.append(("name", "ilike", self.name))
        if self.code:
            domain.append(("code", "ilike", self.code))
        if self.city:
            domain.append(("partner_id.city", "ilike", self.city))
        if self.country:
            domain.append(("partner_id.country_id.name", "ilike", self.country))
        return domain
