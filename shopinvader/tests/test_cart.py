# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields
from odoo.addons.shopinvader import shopinvader_response

from .common import CommonCase


class CartCase(CommonCase):
    """
    Common class for cart tests
    DON'T override it with tests
    """

    def setUp(self):
        super(CartCase, self).setUp()
        self.registry.enter_test_mode()
        self.address = self.env.ref("shopinvader.partner_1_address_1")
        self.fposition = self.env.ref("shopinvader.fiscal_position_2")
        self.default_fposition = self.env.ref("shopinvader.fiscal_position_0")
        self.product_1 = self.env.ref("product.product_product_4b")
        templates = self.env["product.template"].search([])
        templates.write(
            {"taxes_id": [(6, 0, [self.env.ref("shopinvader.tax_1").id])]}
        )
        self.product_1 = self.env.ref("product.product_product_4b")
        self.sale_obj = self.env["sale.order"]

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

    def _install_lang(self, lang_code):
        """
        Install given lang (only if not installed yet)
        :param lang_code: str
        :return: bool
        """
        lang = self.env["res.lang"].search(
            [("code", "=", lang_code), ("active", "=", True)], limit=1
        )
        if not lang:
            wizard = self.env["base.language.install"].create(
                {"lang": lang_code}
            )
            wizard.lang_install()
        return True

    def _change_service_lang(self, lang):
        """
        Change the service lang
        :param lang: str
        :return: service
        """
        self._install_lang(lang)
        context = self.service.env.context.copy()
        context.update({"lang": lang})
        with api.Environment.manage():
            self.env = api.Environment(self.env.cr, self.env.uid, context)
            partner = self.service.partner
            session = self.service.shopinvader_session
            usage = self.service._usage
            with self.work_on_services(
                partner=partner, shopinvader_session=session
            ) as work:
                self.service = work.component(usage=usage)
            return self.service

    def tearDown(self):
        self.registry.leave_test_mode()
        super(CartCase, self).tearDown()


class CartClearTest(object):
    def _check_clear_cart_result(self, cart):
        """
        Check the cart clear.
        :param cart: sale.order recordset
        :return: bool
        """
        cart_id = cart.id
        existing_carts = cart.search([])
        self.service.shopinvader_session.update({"cart_id": cart.id})
        result = self.service.dispatch("clear")
        session = result.get("set_session")
        new_carts = cart.search([("id", "not in", existing_carts.ids)])
        clear_option = self.backend.clear_cart_options
        if clear_option == "clear":
            self.assertFalse(new_carts)
            self.assertEquals(cart_id, cart.exists().id)
            self.assertIsInstance(session, dict)
            self.assertEquals(session.get("cart_id"), cart_id)
            self.assertFalse(cart.order_line)
        elif clear_option == "delete":
            self.assertFalse(cart.exists())
            self.assertIsInstance(session, dict)
            self.assertEquals(session.get("cart_id"), 0)
        elif clear_option == "cancel":
            # We only check that the previous cart is cancelled.
            # The new cart will be created if the customer add a new item.
            # Test the creation of new cart is not the goal of this test.
            self.assertEquals(len(new_carts), 0)
            self.assertIsInstance(session, dict)
            self.assertFalse(session.get("cart_id"))
            # The previous should exists
            self.assertEquals(cart_id, cart.exists().id)
            self.assertEquals(cart.state, "cancel")
        return True

    def test_cart_clear(self):
        self.backend.write({"clear_cart_options": "clear"})
        self._check_clear_cart_result(self.cart)

    def test_cart_delete(self):
        self.backend.write({"clear_cart_options": "delete"})
        self._check_clear_cart_result(self.cart)

    def test_cart_cancel(self):
        self.backend.write({"clear_cart_options": "cancel"})
        self._check_clear_cart_result(self.cart)


class AnonymousCartCase(CartCase, CartClearTest):
    def setUp(self, *args, **kwargs):
        super(AnonymousCartCase, self).setUp(*args, **kwargs)
        self.cart = self.env.ref("shopinvader.sale_order_1")
        self.shopinvader_session = {"cart_id": self.cart.id}
        self.partner = self.backend.anonymous_partner_id
        self.product_1 = self.env.ref("product.product_product_4b")
        self.sale_obj = self.env["sale.order"]
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
        last_external_update_date = self._get_last_external_update_date(cart)
        self._sign_with(partner)
        self._check_last_external_update_date(cart, last_external_update_date)
        self.assertEqual(cart.partner_id, partner)
        self.assertEqual(cart.partner_shipping_id, partner)
        self.assertEqual(cart.partner_invoice_id, partner)
        self.assertEqual(
            cart.pricelist_id, cart.shopinvader_backend_id.pricelist_id
        )

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

    def test_cart_pricelist_apply(self):
        """
        Ensure the pricelist set on the backend is correctly used and applied.
        1) Create a SO manually (using same pricelist as backend) and save the
        amount.
        2) Create a Cart/SO using shopinvader. The pricelist used should be
        the one defined and the price should match with the SO created manually
        just before.
        :return:
        """
        # User must be in this group to fill discount field on SO lines.
        self.env.ref("sale.group_discount_per_so_line").write(
            {"users": [(4, self.env.user.id, False)]}
        )
        # Create 2 pricelists
        pricelist_values = {
            "name": "Custom pricelist 1",
            "discount_policy": "without_discount",
            "item_ids": [
                (
                    0,
                    0,
                    {
                        "applied_on": "1_product",
                        "product_tmpl_id": self.product_1.product_tmpl_id.id,
                        "compute_price": "fixed",
                        "fixed_price": 650,
                    },
                )
            ],
        }
        first_pricelist = self.env["product.pricelist"].create(
            pricelist_values
        )
        pricelist_values = {
            "name": "Custom pricelist 2",
            "discount_policy": "without_discount",
            "item_ids": [
                (
                    0,
                    0,
                    {
                        "applied_on": "1_product",
                        "product_tmpl_id": self.product_1.product_tmpl_id.id,
                        "compute_price": "formula",
                        "base": "pricelist",
                        "price_surcharge": -100,
                        "base_pricelist_id": first_pricelist.id,
                        "date_start": fields.Date.today(),
                        "date_end": fields.Date.today(),
                    },
                )
            ],
        }
        second_pricelist = self.env["product.pricelist"].create(
            pricelist_values
        )
        # First, create the SO manually
        sale = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "partner_shipping_id": self.partner.id,
                "partner_invoice_id": self.partner.id,
                "pricelist_id": second_pricelist.id,
                "typology": "cart",
                "shopinvader_backend_id": self.backend.id,
                "date_order": fields.Datetime.now(),
                "project_id": self.backend.account_analytic_id.id,
            }
        )
        so_line_obj = self.env["sale.order.line"]
        line_values = {
            "order_id": sale.id,
            "product_id": self.product_1.id,
            "product_uom_qty": 1,
            "shopinvader_variant_id": self.product_1.shopinvader_bind_ids.id,
        }
        new_line_values = so_line_obj.play_onchanges(
            line_values, line_values.keys()
        )
        new_line_values.update(line_values)
        line = so_line_obj.create(new_line_values)
        expected_price = line.price_total
        # Then create a new SO/Cart by shopinvader services
        # Force to use this pricelist for the backend
        self.backend.write({"pricelist_id": second_pricelist.id})
        params = {"product_id": self.product_1.id, "item_qty": 1}
        self.service.shopinvader_session.clear()
        add_item_response = self.service.dispatch("add_item", params=params)
        self.service.shopinvader_session.update(
            add_item_response.get("set_session")
        )

        response = self.service.dispatch("search")
        data = response.get("data")
        sale_id = response.get("set_session", {}).get("cart_id")
        sale_order = self.sale_obj.browse(sale_id)
        so_line = fields.first(
            sale_order.order_line.filtered(
                lambda l, p=self.product_1: l.product_id == p
            )
        )
        self.assertEqual(sale_order.pricelist_id, second_pricelist)
        self.assertAlmostEqual(so_line.price_total, expected_price)
        self.assertAlmostEqual(sale_order.amount_total, expected_price)
        self.assertAlmostEqual(
            data.get("lines").get("items")[0].get("amount").get("total"),
            expected_price,
        )
        return

    def test_cart_robustness(self):
        """
        The cart used by the service must always be with typology='cart'
        and state='draft' for the current backend
        If for some reason, these conditions are no more met, the service
        silently create a new cart to replace the one into the session
        """
        cart = self.service._get()
        cart_bis = self.service._get()
        self.assertEqual(cart, cart_bis)
        cart.write({"state": "sale"})
        cart_bis = self.service._get()
        self.assertNotEqual(cart, cart_bis)
        self.assertEqual(cart_bis.typology, "cart")
        self.assertEqual(cart_bis.state, "draft")
        cart = cart_bis
        cart.write({"typology": "sale"})
        cart_bis = self.service._get()
        self.assertNotEqual(cart, cart_bis)

    def test_cart_line_lang_anonymous(self):
        """
        Test the case where the lang (from the front side) is not the same than
        the anonymous partner lang.
        So the current user is the anonymous one. Try to put an item into
        a cart and the sale.order.line name.
        This name value should be into the lang of the user.
        :return:
        """
        params = {"product_id": self.product_1.id, "item_qty": 2}
        # First do it in English (anonymous user lang is the user lang)
        lang = "en_US"
        self.backend.anonymous_partner_id.write({"lang": lang})
        service = self._change_service_lang(lang)
        response = service.dispatch("add_item", params=params)
        sale_id = response.get("set_session", {}).get("cart_id")
        sale_order = self.sale_obj.browse(sale_id)
        so_line = fields.first(
            sale_order.order_line.filtered(
                lambda l, p=self.product_1: l.product_id == p
            )
        )
        product = self.product_1.with_context(lang=lang)
        description_sale_en = product.description_sale
        name_en = product.name
        self.assertIn(description_sale_en, so_line.name)
        self.assertIn(name_en, so_line.name)
        self.assertEquals(self.backend.anonymous_partner_id.lang, lang)
        so_line.unlink()
        previous_lang = lang
        # Then both languages are different
        lang = "fr_FR"
        service = self._change_service_lang(lang)
        product = product.with_context(lang=lang)
        # Force a description in French for the product
        product.write(
            {
                "name": "Un nom de produit en français",
                "description_sale": "Une description de vente en français!",
            }
        )
        description_sale_fr = product.description_sale
        name_fr = product.name
        response = service.dispatch("add_item", params=params)
        sale_id = response.get("set_session", {}).get("cart_id")
        sale_order = self.sale_obj.browse(sale_id)
        so_line = fields.first(
            sale_order.order_line.filtered(
                lambda l, p=product: l.product_id == p
            )
        )
        self.assertIn(description_sale_fr, so_line.name)
        self.assertIn(name_fr, so_line.name)
        self.assertEquals(
            self.backend.anonymous_partner_id.lang, previous_lang
        )
        return

    def test_cart_search_no_create(self):
        """
        - if search is called with a cart_id in session, cart must be returned
        - if search is called without any cart_id in session,
          result must be empty
        """
        self.assertTrue(self.service.shopinvader_session.get("cart_id"))
        search_result = self.service.dispatch("search")
        self.assertEqual(
            search_result["store_cache"]["cart"]["name"], self.cart.name
        )
        # reset cart_id parameter
        shopinvader_response.get().reset()
        self.service.shopinvader_session.update({"cart_id": False})
        search_result = self.service.dispatch("search")
        self.assertDictEqual(search_result, {})


class CommonConnectedCartCase(CartCase):
    """
       Common class for connected cart tests
       DON'T override it with tests
       """

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

    def test_cart_line_lang_logged(self):
        """
        Test the case where the lang (from the front side) is not the same than
        the anonymous partner lang.
        For this case, we are not connected as anonymous user. But this check
        ensure it still working for logged user.
        :return:
        """
        params = {"product_id": self.product_1.id, "item_qty": 2}
        # First, do it in English
        lang = "en_US"
        self.partner.write({"lang": lang})
        service = self._change_service_lang(lang)
        response = service.dispatch("add_item", params=params)
        sale_id = response.get("set_session", {}).get("cart_id")
        sale_order = self.sale_obj.browse(sale_id)
        so_line = fields.first(
            sale_order.order_line.filtered(
                lambda l, p=self.product_1: l.product_id == p
            )
        )
        product = self.product_1.with_context(lang=lang)
        description_sale_en = product.description_sale
        name_en = product.name
        self.assertIn(description_sale_en, so_line.name)
        self.assertIn(name_en, so_line.name)
        so_line.unlink()
        # Then in french
        lang = "fr_FR"
        self._install_lang(lang)
        self.partner.write({"lang": lang})
        service = self._change_service_lang(lang)
        response = service.dispatch("add_item", params=params)
        sale_id = response.get("set_session", {}).get("cart_id")
        sale_order = self.sale_obj.browse(sale_id)
        so_line = fields.first(
            sale_order.order_line.filtered(
                lambda l, p=self.product_1: l.product_id == p
            )
        )
        product = self.product_1.with_context(lang=lang)
        description_sale_fr = product.description_sale
        name_fr = product.name
        self.assertIn(description_sale_fr, so_line.name)
        self.assertIn(name_fr, so_line.name)
        return


class ConnectedCartCase(CommonConnectedCartCase, CartClearTest):
    def test_set_shipping_address(self):
        cart = self.cart
        last_external_update_date = self._get_last_external_update_date(cart)
        self.service.dispatch(
            "update", params={"shipping": {"address": {"id": self.address.id}}}
        )
        self._check_last_external_update_date(cart, last_external_update_date)
        self.assertEqual(cart.partner_id, self.partner)
        self.assertEqual(cart.partner_shipping_id, self.address)
        self.assertEqual(cart.partner_invoice_id, self.address)

    def test_set_invoice_address(self):
        cart = self.cart
        last_external_update_date = self._get_last_external_update_date(cart)
        self.service.dispatch(
            "update",
            params={"invoicing": {"address": {"id": self.address.id}}},
        )
        self._check_last_external_update_date(cart, last_external_update_date)

        self.assertEqual(cart.partner_id, self.partner)
        self.assertEqual(cart.partner_shipping_id, self.partner)
        self.assertEqual(cart.partner_invoice_id, self.address)
        self.assertEqual(
            cart.pricelist_id, cart.shopinvader_backend_id.pricelist_id
        )

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

    def test_cart_robustness(self):
        """
        The cart used by the service must always be with typology='cart'
        and state='draft' for the current backend
        If for some reason, these conditions are no more met, the service
        silently create a new cart to replace the one into the session
        """
        cart = self.service._get()
        cart_bis = self.service._get()
        self.assertEqual(cart, cart_bis)
        cart.write({"state": "sale"})
        cart_bis = self.service._get()
        self.assertNotEqual(cart, cart_bis)
        self.assertEqual(cart_bis.typology, "cart")
        self.assertEqual(cart_bis.state, "draft")
        self.assertEqual(cart_bis.partner_id, self.partner)

    def test_cart_delete_robustness(self):
        """
        If for some reason, the cart does not exist anymore but
        in session, these conditions are no more met, the service
        silently create a new cart to replace the one into the session
        """
        cart = self.service._get()
        cart_bis = self.service._get()
        self.assertEqual(cart, cart_bis)
        cart.unlink()
        cart_bis = self.service._get()
        self.assertNotEqual(cart, cart_bis)
        self.assertEqual(cart_bis.typology, "cart")
        self.assertEqual(cart_bis.state, "draft")
        self.assertEqual(cart_bis.partner_id, self.partner)

    def test_cart_deleted_then_search(self):
        """
        When a user have a cart into session (cart_id) and this cart is
        removed (or doesn't match anymore to be loaded by the service),
        the search shouldn't create a new empty cart.
        This test ensure the search will not create a new cart is this case.
        :return:
        """
        cart = self.service._get()
        # Ensure correctly created
        self.assertTrue(cart.exists())
        # Put the cart into the session
        self.service.shopinvader_session.update({"cart_id": cart.id})
        # Delete the cart
        cart.unlink()
        self.assertFalse(cart.exists())
        nb_sale_order_before = self.cart.search_count([])
        result = self.service.dispatch("search")
        nb_sale_order_after = self.cart.search_count([])
        self.assertDictEqual(result.get("data", {}), {})
        # Ensure no new SO has been created
        self.assertEqual(nb_sale_order_after, nb_sale_order_before)
        return

    def test_writing_note(self):
        res = self.service.dispatch("update", params={"note": "FOO"})
        self.assertIn("note", res["data"])
        self.assertEqual("FOO", res["data"]["note"])


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
