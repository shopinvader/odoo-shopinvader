# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_product.schemas.product import (
    ProductProduct as BaseProductProduct,
)


class ProductProduct(BaseProductProduct, extends=True):
    url_key: str | None = None
    redirect_url_key: list[str] = []

    @classmethod
    def from_product_product(cls, odoo_rec):
        obj = super().from_product_product(odoo_rec)
        # ensure url is up to date
        odoo_rec.product_tmpl_id._update_url_key(lang=odoo_rec.env.context.get("lang"))
        obj.url_key = odoo_rec.url_key or None
        obj.redirect_url_key = odoo_rec.redirect_url_key or []
        return obj
