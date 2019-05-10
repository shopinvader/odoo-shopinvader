# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from .common import CommonCase


class CartCase(CommonCase):
    def setUp(self):
        super(CartCase, self).setUp()
        self.registry.enter_test_mode(self.env.cr)
        self.address = self.env.ref("shopinvader.partner_1_address_1")
        self.fposition = self.env.ref("shopinvader.fiscal_position_2")
        self.default_fposition = self.env.ref("shopinvader.fiscal_position_0")
        templates = self.env["product.template"].search([])
        templates.write(
            {"taxes_id": [(6, 0, [self.env.ref("shopinvader.tax_1").id])]}
        )

    def _create_notification_config(self):
        template = self.env.ref("account.email_template_edi_invoice")
        values = {
            "model_id": self.env.ref("sale.model_sale_order").id,
            "notification_type": "cart_send_email",
            "template_id": template.id,
        }
        self.service.shopinvader_backend.write(
            {"notification_ids": [(0, 0, values)]}
        )

    def tearDown(self):
        self.registry.leave_test_mode()
        super(CartCase, self).tearDown()


class AnonymousCartCase(CartCase):
    def setUp(self, *args, **kwargs):
        super(AnonymousCartCase, self).setUp(*args, **kwargs)
        self.cart = self.env.ref("shopinvader.sale_order_1")
        self.shopinvader_session = {"cart_id": self.cart.id}
        self.partner = self.backend.anonymous_partner_id
        with self.work_on_services(
            partner=None, shopinvader_session=self.shopinvader_session
        ) as work:
            self.service = work.component(usage="cart")

    def _sign_with(self, partner):
        self.service.work.partner = partner
        service_sign = self.service.component("customer")
        service_sign.sign_in()

    def test_anonymous_cart_then_sign(self):
        cart = self.cart
        partner = self.env.ref("shopinvader.partner_1")
        self._sign_with(partner)
        self.assertEqual(cart.partner_id, partner)
        self.assertEqual(cart.partner_shipping_id, partner)
        self.assertEqual(cart.partner_invoice_id, partner)

    def test_ask_email(self):
        """
        Test the ask_email when not logged.
        As the user is not logged, no email should be created
        :return:
        """
        self._create_notification_config()
        now = fields.Date.today()
        self.service.dispatch("ask_email", _id=self.cart.id)
        notif = "cart_send_email"
        description = "Notify {} for {},{}".format(
            notif, self.cart._name, self.cart.id
        )
        domain = [("name", "=", description), ("date_created", ">=", now)]
        # It should not create any queue job because the user is not logged
        self.assertEquals(self.env["queue.job"].search_count(domain), 0)


class CommonConnectedCartCase(CartCase):
    def setUp(self, *args, **kwargs):
        super(CommonConnectedCartCase, self).setUp(*args, **kwargs)
        self.cart = self.env.ref("shopinvader.sale_order_2")
        self.shopinvader_session = {"cart_id": self.cart.id}
        self.partner = self.env.ref("shopinvader.partner_1")
        self.address = self.env.ref("shopinvader.partner_1_address_1")
        with self.work_on_services(
            partner=self.partner, shopinvader_session=self.shopinvader_session
        ) as work:
            self.service = work.component(usage="cart")


class ConnectedCartCase(CommonConnectedCartCase):
    def test_set_shipping_address(self):
        self.service.dispatch(
            "update", params={"shipping": {"address": {"id": self.address.id}}}
        )
        cart = self.cart
        self.assertEqual(cart.partner_id, self.partner)
        self.assertEqual(cart.partner_shipping_id, self.address)
        self.assertEqual(cart.partner_invoice_id, self.address)

    def test_set_invoice_address(self):
        self.service.dispatch(
            "update",
            params={"invoicing": {"address": {"id": self.address.id}}},
        )

        cart = self.cart
        self.assertEqual(cart.partner_id, self.partner)
        self.assertEqual(cart.partner_shipping_id, self.partner)
        self.assertEqual(cart.partner_invoice_id, self.address)

    def test_confirm_cart(self):
        self.assertEqual(self.cart.typology, "cart")
        self.service.dispatch(
            "update", params={"step": {"next": self.backend.last_step_id.code}}
        )
        self.assertEqual(self.cart.typology, "sale")

    def test_confirm_cart_maually(self):
        self.assertEqual(self.cart.typology, "cart")
        self.cart.action_confirm()
        self.assertEqual(self.cart.typology, "sale")

    def test_ask_email1(self):
        """
        Test the ask_email when a user is logged
        As the user logged (and owner of this cart for this case), a new
        queue job should be created to send an email
        :return:
        """
        self._create_notification_config()
        now = fields.Datetime.now()
        self.service.dispatch("ask_email", _id=self.cart.id)
        notif = "cart_send_email"
        description = "Notify {} for {},{}".format(
            notif, self.cart._name, self.cart.id
        )
        domain = [("name", "=", description), ("date_created", ">=", now)]
        self.assertEquals(self.env["queue.job"].search_count(domain), 1)

    def test_ask_email2(self):
        """
        Test the ask_email when a user is logged
        As the user logged (and owner of this cart for this case), a new
        queue job should be created to send an email.
        But for this case we don't add the notification ("event") so nothing
        should happens
        :return:
        """
        now = fields.Datetime.now()
        self.service.dispatch("ask_email", _id=self.cart.id)
        notif = "cart_send_email"
        description = "Notify {} for {},{}".format(
            notif, self.cart._name, self.cart.id
        )
        domain = [("name", "=", description), ("date_created", ">=", now)]
        self.assertEquals(self.env["queue.job"].search_count(domain), 0)

    def test_ask_email3(self):
        """
        Test the ask_email when a user is logged
        As the user logged (and NOT owner of this cart for this case), any
        new queue job should be created.
        :return:
        """
        self._create_notification_config()
        now = fields.Datetime.now()
        self.cart.write({"partner_id": self.partner.copy({}).id})
        self.service.dispatch("ask_email", _id=self.cart.id)
        notif = "cart_send_email"
        description = "Notify {} for {},{}".format(
            notif, self.cart._name, self.cart.id
        )
        domain = [("name", "=", description), ("date_created", ">=", now)]
        self.assertEquals(self.env["queue.job"].search_count(domain), 0)


class ConnectedCartNoTaxCase(CartCase):
    def setUp(self, *args, **kwargs):
        super(ConnectedCartNoTaxCase, self).setUp(*args, **kwargs)
        self.cart = self.env.ref("shopinvader.sale_order_3")
        self.shopinvader_session = {"cart_id": self.cart.id}
        self.partner = self.env.ref("shopinvader.partner_2")
        self.address = self.env.ref("shopinvader.partner_2_address_1")
        with self.work_on_services(
            partner=self.partner, shopinvader_session=self.shopinvader_session
        ) as work:
            self.service = work.component(usage="cart")

    def test_set_shipping_address_with_tax(self):
        cart = self.cart
        # Remove taxes by setting an address without tax
        self.service.dispatch(
            "update", params={"shipping": {"address": {"id": self.partner.id}}}
        )
        self.assertEqual(cart.amount_total, cart.amount_untaxed)
        # Set an address that should have taxes
        self.service.dispatch(
            "update", params={"shipping": {"address": {"id": self.address.id}}}
        )
        self.assertEqual(cart.partner_id, self.partner)
        self.assertEqual(cart.partner_shipping_id, self.address)
        self.assertEqual(cart.partner_invoice_id, self.address)
        self.assertEqual(cart.fiscal_position_id, self.default_fposition)
        self.assertNotEqual(cart.amount_total, cart.amount_untaxed)

    def test_set_shipping_address_without_tax(self):
        cart = self.cart
        self.service.dispatch(
            "update", params={"shipping": {"address": {"id": self.partner.id}}}
        )
        self.assertEqual(cart.partner_id, self.partner)
        self.assertEqual(cart.partner_shipping_id, self.partner)
        self.assertEqual(cart.partner_invoice_id, self.partner)
        self.assertEqual(cart.fiscal_position_id, self.fposition)
        self.assertEqual(cart.amount_total, cart.amount_untaxed)

    def test_edit_shipping_address_without_tax(self):
        cart = self.cart
        # Make an double call to reset the fiscal position with the right value
        self.service.dispatch(
            "update", params={"shipping": {"address": {"id": self.partner.id}}}
        )
        self.service.dispatch(
            "update", params={"shipping": {"address": {"id": self.address.id}}}
        )
        self.assertEqual(cart.partner_id, self.partner)
        self.assertEqual(cart.partner_shipping_id, self.address)
        self.assertEqual(cart.partner_invoice_id, self.address)
        self.assertEqual(cart.fiscal_position_id, self.default_fposition)
        self.assertNotEqual(cart.amount_total, cart.amount_untaxed)

        self.address.write({"country_id": self.env.ref("base.us").id})
        self.assertEqual(cart.partner_id, self.partner)
        self.assertEqual(cart.fiscal_position_id, self.fposition)
        self.assertEqual(cart.amount_total, cart.amount_untaxed)
