from extendable_pydantic import StrictExtendableBaseModel


class Sale(StrictExtendableBaseModel):
    id: int
    state: str

    @classmethod
    def from_sale_order(cls, odoo_rec):
        return cls.model_construct(
            id=odoo_rec.id,
            state=odoo_rec.state,
        )


class Sale1(Sale, extends=True):
    uuid: str | None = None

    @classmethod
    def from_sale_order(cls, odoo_rec):
        res = super().from_sale_order(odoo_rec)
        res.uuid = odoo_rec.uuid or None
        return res


class Sale2(Sale1, extends=True):
    @classmethod
    def from_sale_order(cls, odoo_rec):
        return super().from_sale_order(odoo_rec)


class A:
    pass


a = A()
a.id = 1
a.state = "draft"

sale = Sale.from_sale_order(a)
