# Copyright 2020 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import AbstractComponent


class PackagingServiceMixin(AbstractComponent):
    _name = "shopinvader.packaging.service.mixin"

    def _validator_packaging_info(self):
        return {
            "packaging_id": {
                "coerce": int,
                "nullable": True,
                "required": False,
                "type": "integer",
            },
            "packaging_qty": {
                "coerce": float,
                "type": "float",
                "required": False,
                "nullable": True,
            },
        }

    def _packaging_info_by_qty(self, product, qty):
        return product.with_context(
            **self._packaging_info_ctx()
        ).product_qty_by_packaging(qty, with_contained=True)

    def _packaging_info_ctx(self):
        return {
            # consider only packaging that can be sold
            "_packaging_filter": lambda x: x.can_be_sold,
            # to support multilang shop we rely on packaging type's name
            # which is already translatable.
            "_packaging_name_getter": lambda x: x.packaging_type_id.name,
        }

    def _packaging_values_from_params(self, params):
        if "packaging_id" in params and "packaging_qty" in params:
            return {
                "product_packaging": params.pop("packaging_id"),
                "product_packaging_qty": params.pop("packaging_qty"),
            }
        return {}
