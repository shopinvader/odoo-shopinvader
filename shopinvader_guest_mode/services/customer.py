# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class CustomerService(Component):
    _inherit = "shopinvader.customer.service"
    _usage = "customer"

    def create(self, **params):
        guest = self.component(usage="guest")
        guest._archive_existing_binding(email=params["email"])
        return super().create(**params)
