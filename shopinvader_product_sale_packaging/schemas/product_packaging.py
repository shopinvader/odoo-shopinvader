# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.extendable_fastapi import StrictExtendableBaseModel
from odoo.addons.stock_packaging_calculator.models.product import Packaging


class SimpleProductPackaging(StrictExtendableBaseModel):
    id: int
    name: str
    qty: float
    barcode: str | None = None
    is_unit: bool
    can_be_sold: bool

    @classmethod
    def from_packaging(cls, odoo_product, packaging, packaging_contained_mapping=None):
        # packaging is a either a namedtuple of type Packaging, or a dict with the same keys
        # id key can refer to id of model product.packaging or uom.uom, depending on is_unit
        obj = cls.model_construct(
            id=packaging.id,
            name=packaging.name,
            qty=packaging.qty,
            barcode=packaging.barcode,
            is_unit=packaging.is_unit,
            can_be_sold=not odoo_product.sell_only_by_packaging,
        )
        if not obj.is_unit:
            #  packaging is of type product.packaging, not uom.uom
            # read can_be_sold info on packaging
            pkg = odoo_product.packaging_ids.filtered(lambda p: p.id == packaging.id)
            obj.can_be_sold = pkg.can_be_sold

        return obj


class ProductPackaging(SimpleProductPackaging):
    contained: list[SimpleProductPackaging] = []

    @classmethod
    def from_packaging(cls, odoo_product, packaging, packaging_contained_mapping=None):
        obj = super().from_packaging(odoo_product, packaging)
        if packaging_contained_mapping and not packaging.is_unit:
            contained_packaging = packaging_contained_mapping.get(str(obj.id), [])
            if contained_packaging:
                obj.contained = [
                    SimpleProductPackaging.from_packaging(
                        odoo_product,
                        Packaging(
                            pkg["id"],
                            pkg["name"],
                            pkg["qty"],
                            pkg["barcode"] or None,
                            pkg["is_unit"],
                        ),
                    )
                    for pkg in contained_packaging
                ]
        return obj
