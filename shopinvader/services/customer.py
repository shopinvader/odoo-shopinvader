# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class CustomerService(Component):
    _inherit = 'base.shopinvader.service'
    _name = 'shopinvader.customer.service'
    _usage = 'customer'

    # The following method are 'public' and can be called from the controller.
    def get(self):
        if self.partner:
            address = self.component(usage='address')
            customer = address._to_json(self.partner)[0]
            return {
                'data': customer,
                'store_cache': {'customer': customer},
                }
        else:
            return {'data': {}}

    # The following method are 'private' and should be never never NEVER call
    # from the controller.
    # All params are trusted as they have been checked before

    def _validator_get(self):
        return {}
