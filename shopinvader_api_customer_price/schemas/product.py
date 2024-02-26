# Copyright 2024 Camptocamp SA (https://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from extendable_pydantic import StrictExtendableBaseModel


class ProductPrice(StrictExtendableBaseModel):
    value: float = 0
    tax_included: bool = False
    original_value: float = 0
    discount: float = 0

    @classmethod
    def from_products(cls, records, pricelist=None):
        return {rec.id: rec._get_price(pricelist=pricelist) for rec in records}
