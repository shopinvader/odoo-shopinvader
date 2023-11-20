# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from extendable_pydantic import StrictExtendableBaseModel


class ProductBrand(StrictExtendableBaseModel):
    id: int
    name: str
    sequence: int | None = None
    description: str | None = None
    short_description: str | None = None
    meta_description: str | None = None
    meta_keywords: str | None = None
    seo_title: str | None = None
    url_key: str | None = None
    redirect_url_key: list[str] | None = None

    @classmethod
    def from_product_brand(cls, odoo_rec):
        return cls.model_construct(
            id=odoo_rec.id,
            name=odoo_rec.name,
            sequence=odoo_rec.sequence or None,
            description=odoo_rec.description or None,
            short_description=odoo_rec.short_description or None,
            meta_description=odoo_rec.meta_description or None,
            meta_keywords=odoo_rec.meta_keywords or None,
            seo_title=odoo_rec.seo_title or None,
            url_key=odoo_rec.url_key or None,
            redirect_url_key=odoo_rec.redirect_url_key or None,
        )
