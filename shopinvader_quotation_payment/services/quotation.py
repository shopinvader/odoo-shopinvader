# -*- coding: utf-8 -*-
# Copyright 2016 Akretion (http://www.akretion.com)
# Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo.addons.component.core import Component
from odoo.exceptions import UserError
from odoo.tools.translate import _

class QuotationService(Component):
    _inherit = [
        'shopinvader.quotation.service',
        'shopinvader.abstract.payment.service'
    ]
    _name = 'shopinvader.quotation.service'

    def add_payment(self, _id, **params):
        quotation = self._get(_id)
        if not quotation:
            raise UserError(_('There is not quotation'))
        elif quotation.state != 'sent':
            raise UserError(_('The quotation is not validated'))
        else:
            self._set_payment_mode(quotation, params)
            provider_name = quotation.payment_mode_id.provider
            if provider_name:
                return self._process_payment_provider(
                    provider_name, quotation, params[provider_name])
            else:
                return self._confirm_cart(quotation)
