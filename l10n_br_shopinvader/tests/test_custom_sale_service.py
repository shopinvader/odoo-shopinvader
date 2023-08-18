# Copyright 2020 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.shopinvader.tests.common import CommonCase


class CustomSaleServiceTest(CommonCase):
    def setUp(self):
        super().setUp()
        # for the Test we simulate that the customer logged is shopinvader.partner_1
        self.partner = self.env.ref("shopinvader.partner_1")
        with self.work_on_services(partner=self.partner) as work:
            # we init the service that we will use in the test
            self.sale_service = work.component(usage="sales")

    def test_read_custom_field(self):
        # I take a sale order that belong to the partner shopinvader.partner_1
        sale = self.env.ref("shopinvader.sale_order_2")

        # Note as this sale is not yet confirm (it's still a cart I confirm it)
        sale.action_confirm_cart()

        # I write in the custom_field
        # sale.write({"custom_field": "foo"})

        # Now I call the rest api by calling the get method on the sale service
        api_response = self.sale_service.dispatch("get", sale.id)
        # The result should include my custom_field
        self.assertIn("custom_field", api_response)
        self.assertEqual(api_response["custom_field"], "foo")

    def test_action_on_sale_order(self):
        # I take a sale order that belong to the partner shopinvader.partner_1
        sale = self.env.ref("shopinvader.sale_order_2")

        # Note as this sale is not yet confirm (it's still a cart I confirm it)
        sale.action_confirm_cart()

        self.sale_service.dispatch("custom_action", sale.id, params={})

        self.assertEqual(sale.custom_action_done, True)
