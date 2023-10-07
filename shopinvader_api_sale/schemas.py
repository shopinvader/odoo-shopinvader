# Copyright 2023 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.extendable_fastapi import StrictExtendableBaseModel


class SaleSearch(StrictExtendableBaseModel):
    name: str | None = None
    typology: str | None = "sale"

    def to_domain(self):
        domain = []
        if self.name:
            domain.append(("name", "ilike", self.name))
        if self.typology:
            domain.append(("typology", "=", self.typology))
        return domain
