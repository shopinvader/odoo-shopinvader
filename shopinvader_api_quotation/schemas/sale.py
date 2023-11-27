from extendable_pydantic import StrictExtendableBaseModel

from odoo.addons.shopinvader_schema_sale.schemas.sale import Sale


class Sale(Sale, extends=True):
    available_for_quotation: bool | None = None
    shop_only_quotation: bool | None = None
    customer_ref: str | None = None

    @classmethod
    def from_sale_order(cls, odoo_rec):
        res = super().from_sale_order(odoo_rec)
        res.available_for_quotation = True
        res.shop_only_quotation = odoo_rec.shop_only_quotation
        res.customer_ref = odoo_rec.client_order_ref or None
        # res.shop_only_quotation = any(
        #     odoo_rec.order_line.product_id.mapped("shop_only_quotation")
        # ) mettre un champs calculé coté odoo sur model sale_order
        return res


class QuotationUpdateInput(StrictExtendableBaseModel):
    customer_ref: str | None = None

    def to_sale_order_vals(self) -> dict:
        return {"client_order_ref": self.customer_ref}
