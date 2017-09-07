# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from ..services.cart import CartService
from .common import CommonCase
from openerp.addons.connector.tests.common import mock_job_delay_to_direct


class NotificationCartCase(CommonCase):

    def setUp(self):
        super(NotificationCartCase, self).setUp()
        self.cart = self.env.ref('shopinvader.sale_order_2')
        self.partner = self.env.ref('shopinvader.partner_1')
        self.shopinvader_session = {'cart_id': self.cart.id}
        self.service = self._get_service(CartService, self.partner)
        self.payment_method =\
            self.env.ref('shopinvader.payment_method_banktransfert')
        self.shopinvader_payment_method =\
            self.env.ref('shopinvader.shopinvader_payment_banktransfert')
        self.job_path =\
            'openerp.addons.shopinvader.models.backend.send_notification'

    def _check_notification(self, notif_type, exist=True):
        if notif_type == 'cart':
            subject = 'Cart notification %s' % self.cart.name
        else:
            subject = 'Sale notification %s' % self.cart.name
        message = self.env['mail.message'].search([('subject', '=', subject)])
        self.assertEqual(len(message), int(exist))

    def _set_payment_method(self):
        with mock_job_delay_to_direct(self.job_path):
            self.service.update({
                'payment_method_id': self.payment_method.id,
                'next_step': self.backend.last_step_id.code})

    def confirm_sale(self):
        with mock_job_delay_to_direct(self.job_path):
            self.cart.action_button_confirm()

    def test_notification_cart_and_sale(self):
        self._set_payment_method()
        self.assertEqual(self.cart.typology, 'sale')
        self._check_notification('cart', exist=True)

        self.confirm_sale()
        self._check_notification('sale', exist=True)

    def test_notification_only_sale(self):
        self.shopinvader_payment_method.notification = 'sale_confirmation'
        self._set_payment_method()
        self.assertEqual(self.cart.typology, 'sale')
        self._check_notification('cart', exist=False)

        self.confirm_sale()
        self._check_notification('sale', exist=True)

    def test_notification_only_cart(self):
        self.shopinvader_payment_method.notification = 'cart_confirmation'
        self._set_payment_method()
        self.assertEqual(self.cart.typology, 'sale')
        self._check_notification('cart', exist=True)

        self.confirm_sale()
        self._check_notification('sale', exist=False)
