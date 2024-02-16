# Copyright 2021 David BEAL @ Akretion
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class CustomerService(Component):
    _inherit = "shopinvader.customer.service"

    def _validator_create_non_required_address_keys(self):
        res = super()._validator_create_non_required_address_keys()
        res.append("street3")
        return res
