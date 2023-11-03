# Copyright 2023 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from extendable_pydantic import StrictExtendableBaseModel


class SaleLineOption(StrictExtendableBaseModel):
    @classmethod
    def _prepare_from_sale_line(cls, line):
        return {}

    @classmethod
    def from_sale_line(cls, line):
        return cls.model_validate(cls._prepare_from_sale_line(line))
