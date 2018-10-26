# -*- coding: utf-8 -*-
# Copyright 2016 Akretion (http://www.akretion.com)
# Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo.addons.component.core import Component
from odoo.exceptions import UserError
from odoo.tools.translate import _


class QuotationService(Component):
    _inherit = [
        'shopinvader.abstract.payment.service',
        'shopinvader.quotation.service'
    ]
    _name = 'shopinvader.quotation.service'

    def _load_target(self, params):
        """

        :param params: dict
        :return: exposed model recordset
        """
        _id = params.get('_id')
        return self._get(_id=_id)

    def _add_payment(self, quotation, params):
        if not quotation:
            raise UserError(_('There is not quotation'))
        elif quotation.state != 'sent':
            raise UserError(_('The quotation is not validated'))
        return super(QuotationService, self)._add_payment(quotation, params)

    def _action_after_payment(self, target):
        """
        Confirm the cart after the payment
        :param target: payment recordset
        :return: dict
        """
        values = super(QuotationService, self)._action_after_payment(target)
        values.update(self._confirm_cart(target))
        return values
