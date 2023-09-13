from extendable_pydantic import ExtendableModelMeta
from pydantic import BaseModel


class IdAndNameInfo(BaseModel, metaclass=ExtendableModelMeta):
    id: int
    name: str

    @classmethod
    def from_rec(cls, odoo_rec):
        if not odoo_rec:
            return
        return cls.model_construct(
            id=odoo_rec.id,
            name=odoo_rec.name,
        )


class IdRequest(BaseModel, metaclass=ExtendableModelMeta):
    id: int

    @classmethod
    def from_rec(cls, odoo_rec):
        if not odoo_rec:
            return
        return cls.model_construct(
            id=odoo_rec.id,
        )
