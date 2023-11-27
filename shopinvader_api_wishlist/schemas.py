# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from __future__ import annotations

from typing import Annotated, Generic, TypeVar

from extendable_pydantic.models import StrictExtendableBaseModel
from pydantic import Field

from odoo import api

from odoo.addons.base.models.res_partner import Partner
from odoo.addons.product_set.models.product_set_line import ProductSetLine
from odoo.addons.sale_wishlist.models.product_set import ProductSet


class WishlistLine(StrictExtendableBaseModel):
    id: int
    sequence: int
    product_id: int
    quantity: float

    @classmethod
    def from_product_set_line(
        cls, line: ProductSetLine
    ) -> self:  # noqa: F821  pylint: disable=undefined-variable
        return cls.model_construct(
            id=line.id,
            sequence=line.sequence,
            product_id=line.product_id.id,
            quantity=line.quantity,
        )


class WhishlistPartnerRef(StrictExtendableBaseModel):
    id: int
    name: str

    @classmethod
    def from_res_partner(
        cls, partner: Partner
    ) -> self:  # noqa: F821  pylint: disable=undefined-variable
        return cls.model_construct(
            id=partner.id,
            name=partner.name,
        )


class Wishlist(StrictExtendableBaseModel):
    name: str
    lines: list[WishlistLine] = []
    partner: WhishlistPartnerRef | None
    ref: str | None
    id: int
    typology: str

    @classmethod
    def from_product_set(
        cls, odoo_rec: ProductSet
    ) -> self:  # noqa: F821  pylint: disable=undefined-variable
        record = cls.model_construct(
            id=odoo_rec.id,
            name=odoo_rec.name,
            lines=[
                WishlistLine.from_product_set_line(line)
                for line in odoo_rec.set_line_ids
            ],
            ref=odoo_rec.ref or None,
            typology=odoo_rec.typology,
        )
        if odoo_rec.partner_id:
            record.partner = WhishlistPartnerRef.from_res_partner(odoo_rec.partner_id)
        return record


class WishlistLineCreateRequest(StrictExtendableBaseModel, extra="ignore"):
    sequence: int | None = None
    product_id: int
    quantity: float | None = 1.0

    def to_product_set_line_vals(self, env: api.Environment) -> dict:
        return {
            "sequence": self.sequence,
            "product_id": self.product_id,
            "quantity": self.quantity,
        }


class WishlistCreateRequest(StrictExtendableBaseModel, extra="ignore"):
    name: str
    lines: list[WishlistLineCreateRequest] | None = None
    ref: str | None = None
    typology: str | None = "wishlist"

    def to_product_set_vals(self, env: api.Environment) -> dict:
        vals = {
            "name": self.name,
            "typology": self.typology,
            "ref": self.ref,
        }
        if self.lines:
            vals["set_line_ids"] = [
                (0, 0, line.to_product_set_line_vals(env)) for line in self.lines
            ]
        return vals


class WishlistUpdateRequest(StrictExtendableBaseModel, extra="ignore"):
    name: str | None = None
    lines: list[WishlistLineCreateRequest] | None = None
    ref: str | None = None
    typology: str = None

    def to_product_set_vals(self, env: api.Environment) -> dict:
        values = self.model_dump(exclude_unset=True)
        vals = {}
        if "name" in values:
            vals["name"] = self.name
        if "ref" in values:
            vals["ref"] = self.ref
        if "lines" in values:
            vals["set_line_ids"] = [
                (0, 0, line.to_product_set_line_vals(env)) for line in self.lines
            ]
            # insert a delete all lines command at the beginning to remove all
            # lines since we are replacing them
            vals["set_line_ids"].insert(0, (5, 0, 0))
        if "typology" in values:
            vals["typology"] = self.typology
        return vals


class WishlistLineIdentifier(StrictExtendableBaseModel):
    product_id: int

    def __hash__(self):
        return hash((type(self), self.product_id))


class WishlistDeleteItemRequest(WishlistLineIdentifier, extra="ignore"):
    ...


class WishlistdMoveItemRequest(WishlistLineIdentifier, extra="ignore"):
    move_to_wishlist_id: int


class WishlistAddItemRequest(WishlistLineIdentifier, extra="ignore"):
    product_id: int
    quantity: float | None = 1.0
    sequence: int | None = None

    def to_product_set_line_vals(self, env: api.Environment) -> dict:
        values = self.model_dump(exclude_unset=True)
        vals = {"product_id": self.product_id, "quantity": self.quantity}
        if "sequence" in values:
            vals["sequence"] = self.sequence
        return vals


class WishlistUpdateItemRequest(WishlistAddItemRequest, extra="ignore"):
    ...


class WishlistReplaceItemRequest(WishlistLineIdentifier, extra="ignore"):
    product_id: int
    replacement_product_id: int


class WishlistSearchRequest(StrictExtendableBaseModel, extra="ignore"):
    id: int | None = None
    name: Annotated[
        str | None,
        Field(
            description="When used, a 'case insensitive like' operator is used "
            "to query the database."
        ),
    ] = None
    ref: Annotated[
        str | None,
        Field(
            description="When used, an equal operator is used to query the " "database."
        ),
    ] = None

    def to_odoo_domain(self, env: api.Environment) -> list:
        domain = []
        if self.id:
            domain.append(("id", "=", self.id))
        if self.name:
            domain.append(("name", "ilike", self.name))
        if self.ref:
            domain.append(("ref", "=", self.ref))
        return domain


class WishlistItemToCartRequest(StrictExtendableBaseModel, extra="ignore"):
    product_id: int


class WishlistAddItemsToCartRequest(StrictExtendableBaseModel, extra="ignore"):
    uuid: str | None = None
    lines: list[WishlistItemToCartRequest] = []


class WishlistAddToCartRequest(StrictExtendableBaseModel, extra="ignore"):
    uuid: str | None = None


T = TypeVar("T")


class WishlistLines(StrictExtendableBaseModel, Generic[T]):
    lines: list[T] = []
