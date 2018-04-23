# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.addons.component.core import Component


class ShopInvaderCustomerService(Component):
    _inherit = 'shopinvader.customer.service'

    def _create_shopinvader_binding(self, external_id):
        """
        Inherit the creation of shopinvader binding to add the sale profile
        code of the shopinvader partner
        :param external_id: int
        :return: dict
        """
        response = super(ShopInvaderCustomerService, self)\
            ._create_shopinvader_binding(external_id=external_id)
        data = response.get('data', {})
        # Get the shopinvader partner created into the super
        shop_partner = self.env['shopinvader.partner'].search([
            ('backend_id', '=', self.locomotive_backend.id),
            ('external_id', '=', external_id),
            ('record_id', '=', self.partner.id),
        ], order="create_date desc", limit=1)
        data.update({
            'sale_profile': shop_partner.sale_profile_id.code,
        })
        return response
