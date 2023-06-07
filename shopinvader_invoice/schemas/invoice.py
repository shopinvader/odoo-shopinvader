# Copyright 2023 Akretion (https://www.akretion.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from extendable_pydantic import ExtendableModelMeta
import pydantic
from pydantic import BaseModel  # pylint: disable=missing-manifest-dependency

from odoo.api import Environment
from odoo.addons.fastapi.depends import paging, authenticated_partner_env
from odoo.addons.fastapi.schemas import PagedCollection, Paging


class Amount(BaseModel, metaclass=ExtendableModelMeta):
    amount_tax: float | None
    amount_untaxed: float | None
    amount_total: float | None
    amount_due: : float = pydantic.Field(alias="amount_residual") | None


class AccountMove(BaseModel, metaclass=ExtendableModelMeta):
    id: int
    name: str
    payment_reference: str
    date_invoice: str = pydantic.Field(alias="invoice_date")
    date_due: str = pydantic.Field(alias="invoice_date_due") | None
    amount: Amount | None
    type: str = pydantic.Field(alias="move_type")
    state: str
    payment_state: str
