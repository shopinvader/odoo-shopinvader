# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class CustomerService(Component):
    _inherit = "shopinvader.customer.service"

    def search(self, **params):
        """
        This method is called by locomotive if no account is found into the
        cache when accessing to store.customer into a template
        """
        return {"data": {}}

    def _validator_search(self):
        return {}
