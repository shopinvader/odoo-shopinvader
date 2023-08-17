# Copyright 2020 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.shopinvader.tests.common import CommonCase


class CustomAddressServiceTest(CommonCase):
    def setUp(self):
        super().setUp()
        # for the Test we simulate that the customer logged is shopinvader.partner_1
        self.partner = self.env.ref("shopinvader.partner_1")
        with self.work_on_services(partner=self.partner) as work:
            # we init the service that we will use in the test
            self.address_service = work.component(usage="addresses")

    def test_read_custom_field(self):
        self.partner.write({"custom_field": "foo"})

        # Now I call the rest api by calling the get method on address
        api_response = self.address_service.dispatch("get", self.partner.id)[0]
        # The result should include my custom_field
        self.assertIn("custom_field", api_response)
        self.assertEqual(api_response["custom_field"], "foo")

    def test_write_custom_field(self):
        self.address_service.dispatch(
            "update", self.partner.id, params={"custom_field": "foo"}
        )
        self.assertEqual(self.partner.custom_field, "foo")

    def test_create_address_with_custom_field(self):
        self.address_service.dispatch(
            "create",
            params={
                "name": "Bar",
                "street": "Shopinvader Street",
                "zip": "69100",
                "city": "Lyon",
                "country": {"id": self.ref("base.fr")},
                "custom_field": "foo",
            },
        )
        address = self.env["res.partner"].search(
            [("parent_id", "=", self.partner.id), ("name", "=", "Bar")]
        )
        self.assertEqual(address.custom_field, "foo")
