# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import CommonCarrierCase


class CarrierCase(CommonCarrierCase):
    def setUp(self):
        super(CarrierCase, self).setUp()
        self.carrier_service = self.service.component("delivery_carrier")

    def test_available_carriers(self):
        response = self.service.dispatch("get_delivery_methods")
        self.assertEqual(len(response), 2)

    def test_deprecated_apply_delivery_method(self):
        cart = self._apply_delivery_method(self.free_carrier)
        self.assertEqual(cart["shipping"]["amount"]["total"], 0)

    def test_setting_free_carrier(self):
        cart = self._set_carrier(self.free_carrier)
        self.assertEqual(cart["shipping"]["amount"]["total"], 0)
        self.assertEqual(
            cart["shipping"]["selected_carrier"],
            {
                "description": self.free_carrier.description or None,
                "id": self.free_carrier.id,
                "name": self.free_carrier.name,
                "code": self.free_carrier.code,
                "type": None,
            },
        )

    def test_setting_poste_carrier(self):
        cart = self._set_carrier(self.poste_carrier)
        # Check shipping amount
        cart_ship = cart.get("shipping")
        self.assertEqual(cart_ship["amount"]["total"], 20)
        self.assertEqual(cart_ship["amount"]["untaxed"], 17.39)
        self.assertEqual(cart_ship["amount"]["tax"], 2.61)

        # Check items amount
        self.assertEqual(cart["lines"]["amount"]["total"], 8555.0)
        self.assertEqual(cart["lines"]["amount"]["untaxed"], 8555.0)
        self.assertEqual(cart["lines"]["amount"]["tax"], 0)

        # Check total amount
        self.assertEqual(cart["amount"]["total"], 8575.0)
        self.assertEqual(cart["amount"]["untaxed"], 8572.39)
        self.assertEqual(cart["amount"]["tax"], 2.61)

        # Check totals without shipping prices
        cart_amount = cart.get("amount")
        total_without_shipping = (
            cart_amount["total"] - cart_ship["amount"]["total"]
        )
        untaxed_without_shipping = (
            cart_amount["untaxed"] - cart_ship["amount"]["untaxed"]
        )
        tax_without_shipping = cart_amount["tax"] - cart_ship["amount"]["tax"]
        self.assertEqual(
            cart_amount["total_without_shipping"], total_without_shipping
        )
        self.assertEqual(
            cart_amount["untaxed_without_shipping"], untaxed_without_shipping
        )
        self.assertEqual(
            cart_amount["tax_without_shipping"], tax_without_shipping
        )

        # Check Selected carrier
        self.assertEqual(
            cart["shipping"]["selected_carrier"],
            {
                "description": self.poste_carrier.description or None,
                "id": self.poste_carrier.id,
                "name": self.poste_carrier.name,
                "code": self.poste_carrier.code,
                "type": None,
            },
        )

    def test_reset_carrier_on_add_item(self):
        self._apply_carrier_and_assert_set()
        cart = self.add_item(self.product_1.id, 2)
        self.assertEqual(cart["shipping"]["amount"]["total"], 0)
        self.assertFalse(cart["shipping"]["selected_carrier"])

    def test_reset_carrier_on_update_item(self):
        cart = self._apply_carrier_and_assert_set()
        items = cart["lines"]["items"]
        cart = self.update_item(items[0]["id"], 1)
        self.assertEqual(cart["shipping"]["amount"]["total"], 0)
        self.assertFalse(cart["shipping"]["selected_carrier"])

    def test_reset_carrier_on_delete_item(self):
        cart = self._apply_carrier_and_assert_set()
        items = cart["lines"]["items"]
        cart = self.delete_item(items[0]["id"])
        self.assertEqual(cart["shipping"]["amount"]["total"], 0)
        self.assertFalse(cart["shipping"]["selected_carrier"])

    def test_reset_carrier_on_changing_delivery_address(self):
        self._apply_carrier_and_assert_set()
        cart = self.service.dispatch(
            "update", params={"shipping": {"address": {"id": self.address.id}}}
        )["data"]
        self.assertEqual(cart["shipping"]["amount"]["total"], 0)
        self.assertFalse(cart["shipping"]["selected_carrier"])

    def test_get_cart_price_by_country1(self):
        """
        Check the service get_cart_price_by_country.
        For this case, the cart doesn't have an existing delivery line.
        :return:
        """
        french_country = self.env.ref("base.fr")
        belgium = self.env.ref("base.be")
        self.backend.carrier_ids.write(
            {"country_ids": [(6, False, [belgium.id, french_country.id])]}
        )
        partner = self.service.partner
        # Use the partner of the service
        self.cart.write({"partner_id": partner.id})
        partner.write({"country_id": False})
        self.cart.write({"carrier_id": False})
        # Force load every fields
        self.cart.read()
        cart_values_before = self.cart._convert_to_write(self.cart._cache)
        lines = {}
        for line in self.cart.order_line:
            line.read()
            lines.update({line.id: line._convert_to_write(line._cache)})
        nb_lines_before = self.env["sale.order.line"].search_count([])
        self.service.shopinvader_session.update({"cart_id": self.cart.id})
        params = {"country_id": belgium.id, "target": "current_cart"}
        result = self.carrier_service.dispatch("search", params=params)
        self.cart.read()
        cart_values_after = self.cart._convert_to_write(self.cart._cache)
        nb_lines_after = self.env["sale.order.line"].search_count([])
        self.assertDictEqual(cart_values_before, cart_values_after)
        self.assertEquals(nb_lines_after, nb_lines_before)

        partner.write({"country_id": french_country.id})
        self.cart.write({"carrier_id": self.poste_carrier.id})
        # Force load every fields
        self.cart.read()
        cart_values_before = self.cart._convert_to_write(self.cart._cache)
        lines = {}
        for line in self.cart.order_line:
            line.read()
            lines.update({line.id: line._convert_to_write(line._cache)})
        nb_lines_before = self.env["sale.order.line"].search_count([])
        self.service.shopinvader_session.update({"cart_id": self.cart.id})
        params = {"country_id": belgium.id, "target": "current_cart"}
        result = self.carrier_service.dispatch("search", params=params)
        self.assertEquals(self.cart.name, cart_values_before.get("name", ""))
        self.cart.read()
        cart_values_after = self.cart._convert_to_write(self.cart._cache)
        self.assertDictEqual(cart_values_before, cart_values_after)
        nb_lines_after = self.env["sale.order.line"].search_count([])
        self.assertEquals(nb_lines_after, nb_lines_before)
        # Ensure lines still ok
        self.assertEquals(len(lines), len(self.cart.order_line))
        for line_id, line_values in lines.iteritems():
            order_line = self.cart.order_line.filtered(
                lambda l, lid=line_id: l.id == lid
            )
            order_line.read()
            self.assertDictEqual(
                order_line._convert_to_write(order_line._cache), line_values
            )
        self.assertEquals(self.cart.partner_id, partner)
        self.assertEquals(french_country, partner.country_id)
        self._check_carriers(result)

    def test_get_cart_price_by_country_anonymous(self):
        """
        Check the service get_cart_price_by_country.
        For this case, the cart doesn't have an existing delivery line.
        :return:
        """
        with self.work_on_services(
            partner=self.backend.anonymous_partner_id, shopinvader_session={}
        ) as work:
            self.service = work.component(usage="cart")
        # Update with anonymous user
        self.test_get_cart_price_by_country1()

    def _check_carriers(self, result):
        """
        Check carrier for current cart based on given result list of dict.
        :param result: list of dict
        :return: bool
        """
        available_carriers = self.backend.carrier_ids.with_context(
            order_id=self.cart.id
        ).filtered(lambda c: c.available)
        carrier_rows = result.get("rows")
        self.assertEquals(len(available_carriers), len(carrier_rows))
        for carrier_result in carrier_rows:
            carrier = available_carriers.filtered(
                lambda c: c.id == carrier_result.get("id")
            )
            self.assertEquals(len(carrier), 1)
            self.assertEquals(carrier.name, carrier_result.get("name"))
            self.assertAlmostEquals(
                carrier.price,
                carrier_result.get("price"),
                places=self.precision,
            )
        return True

    def test_get_cart_price_by_country2(self):
        """
        Check the service get_cart_price_by_country.
        For this case, the cart have 1 delivery line set
        :return:
        """
        french_country = self.env.ref("base.fr")
        belgium = self.env.ref("base.be")
        partner = self.cart.partner_id
        partner.write({"country_id": french_country.id})
        self.cart.write({"carrier_id": self.poste_carrier.id})
        self.cart.delivery_set()
        # Force load every fields
        self.cart.read()
        cart_values_before = self.cart._convert_to_write(self.cart._cache)
        cart_values_before.pop("order_line", None)
        lines = {}
        for line in self.cart.order_line:
            line.read()
            lines.update({line.id: line._convert_to_write(line._cache)})
        nb_lines_before = self.env["sale.order.line"].search_count([])
        self.service.shopinvader_session.update({"cart_id": self.cart.id})
        params = {"country_id": belgium.id, "target": "current_cart"}
        result = self.carrier_service.dispatch("search", params=params)
        self.assertEquals(self.cart.name, cart_values_before.get("name", ""))
        self.cart.read()
        cart_values_after = self.cart._convert_to_write(self.cart._cache)
        cart_values_after.pop("order_line", None)
        self.assertDictEqual(cart_values_before, cart_values_after)
        nb_lines_after = self.env["sale.order.line"].search_count([])
        self.assertEquals(nb_lines_after, nb_lines_before)
        # Ensure lines still ok
        self.assertEquals(len(lines), len(self.cart.order_line))
        for line_id, line_values in lines.iteritems():
            order_line = self.cart.order_line.filtered(
                lambda l, lid=line_id: l.id == lid
            )
            # Because delivery line has changed and the ID doesn't match
            # anymore.
            # But should still similar!
            if not order_line:
                order_line = self.cart.order_line.filtered(
                    lambda l: l.is_delivery
                )
            order_line.read()
            self.assertDictEqual(
                order_line._convert_to_write(order_line._cache), line_values
            )
        self.assertEquals(self.cart.partner_id, partner)
        self.assertEquals(french_country, partner.country_id)
        self._check_carriers(result)

    def test_get_cart_price_by_country3(self):
        """
        Check the service get_cart_price_by_country.
        For this case, the cart have 1 delivery line set
        The cart doesn't have a carrier set.
        :return:
        """
        french_country = self.env.ref("base.fr")
        belgium = self.env.ref("base.be")
        partner = self.cart.partner_id
        partner.write({"country_id": french_country.id})
        self.assertFalse(self.cart.carrier_id)
        # Force load every fields
        self.cart.read()
        cart_values_before = self.cart._convert_to_write(self.cart._cache)
        cart_values_before.pop("order_line", None)
        lines = {}
        for line in self.cart.order_line:
            line.read()
            lines.update({line.id: line._convert_to_write(line._cache)})
        nb_lines_before = self.env["sale.order.line"].search_count([])
        self.service.shopinvader_session.update({"cart_id": self.cart.id})
        params = {"country_id": belgium.id, "target": "current_cart"}
        result = self.carrier_service.dispatch("search", params=params)
        self.assertEquals(self.cart.name, cart_values_before.get("name", ""))
        self.cart.read()
        cart_values_after = self.cart._convert_to_write(self.cart._cache)
        cart_values_after.pop("order_line", None)
        self.assertDictEqual(cart_values_before, cart_values_after)
        nb_lines_after = self.env["sale.order.line"].search_count([])
        self.assertEquals(nb_lines_after, nb_lines_before)
        # Ensure lines still ok
        self.assertEquals(len(lines), len(self.cart.order_line))
        for line_id, line_values in lines.iteritems():
            order_line = self.cart.order_line.filtered(
                lambda l, lid=line_id: l.id == lid
            )
            order_line.read()
            self.assertDictEqual(
                order_line._convert_to_write(order_line._cache), line_values
            )
        self.assertEquals(self.cart.partner_id, partner)
        self.assertEquals(french_country, partner.country_id)
        self._check_carriers(result)

    def test_total_without_shipping_without_discount(self):
        self.cart.order_line[0].discount = 10
        self.assertEqual(self.cart.discount_total, 265.5)
        cart = self._set_carrier(self.poste_carrier)
        cart_amount = cart.get("amount")
        cart_ship = cart.get("shipping")

        total_without_shipping = (
            cart_amount["total"] - cart_ship["amount"]["total"]
        )
        untaxed_without_shipping = (
            cart_amount["untaxed"] - cart_ship["amount"]["untaxed"]
        )
        tax_without_shipping = cart_amount["tax"] - cart_ship["amount"]["tax"]
        self.assertEqual(
            cart_amount["total_without_shipping"], total_without_shipping
        )
        self.assertEqual(
            cart_amount["untaxed_without_shipping"], untaxed_without_shipping
        )
        self.assertEqual(
            cart_amount["tax_without_shipping"], tax_without_shipping
        )

        total_without_shipping_without_discount = (
            total_without_shipping - cart_amount["discount_total"]
        )
        self.assertEqual(
            cart_amount["total_without_shipping_without_discount"],
            total_without_shipping_without_discount,
        )
