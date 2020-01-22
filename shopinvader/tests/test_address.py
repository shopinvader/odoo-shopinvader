# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import AccessError, UserError

from .common import CommonCase


def _check_partner_data(self, partner, data, skip_keys=None):
    compare_data = {}
    skip_keys = skip_keys or ("external_id", "partner_email")
    for key, value in data.items():
        odoo_key = key
        if key in skip_keys:
            continue
        elif key in ("country", "state", "title", "industry_id"):
            value = value["id"]
        if key in ("country", "state"):
            odoo_key = key + "_id"
        compare_data[odoo_key] = value
    self.assertRecordValues(partner, [compare_data])


class CommonAddressCase(CommonCase):
    @classmethod
    def setUpClass(cls):
        super(CommonAddressCase, cls).setUpClass()
        cls.partner = cls.env.ref("shopinvader.partner_1")
        cls.address = cls.env.ref("shopinvader.partner_1_address_1")
        cls.address_2 = cls.env.ref("shopinvader.partner_1_address_2")
        cls.address_params = {
            "name": "Purple",
            "street": "Rue du jardin",
            "zip": "43110",
            "city": "Aurec sur Loire",
            "phone": "0485485454",
            "country": {"id": cls.env.ref("base.fr").id},
        }

    def setUp(self, *args, **kwargs):
        super(CommonAddressCase, self).setUp(*args, **kwargs)
        with self.work_on_services(partner=self.partner) as work:
            self.address_service = work.component(usage="addresses")

    def check_data(self, address, data):
        _check_partner_data(self, address, data)


class AddressTestCase(object):
    def _test_create_address(self, params, expected):
        existing = [
            address["id"] for address in self.address_service.search()["data"]
        ]
        address_list = self.address_service.dispatch("create", params=params)[
            "data"
        ]
        created_id = [
            address["id"]
            for address in address_list
            if address["id"] not in existing
        ][0]
        address = self.env["res.partner"].browse(created_id)
        self.check_data(address, expected)

    def test_create_address(self):
        # no email, verify defaults
        params = dict(self.address_params, parent_id=self.partner.id)
        # type defaults to `other`
        expected = dict(params)
        self._test_create_address(params, expected)
        # pass email and type
        params = dict(params, email="purple@test.oca", type="invoice")
        expected = dict(params)
        self._test_create_address(params, expected)

    def _test_update_address(self, address_id, params, expected):
        self.address_service.dispatch("update", address_id, params=params)
        address = self.env["res.partner"].browse(address_id)
        self.check_data(address, expected)

    def test_add_address_invoice(self):
        # Create an invoice address with wrong type
        # Check raise
        # Create an invoice address with invoice type
        # Check data
        self.address_params.update({"type": "wrong"})
        address_ids = [
            address["id"] for address in self.address_service.search()["data"]
        ]
        with self.assertRaises(UserError):
            self.address_service.dispatch(
                "create", params=self.address_params
            )["data"]
        self.address_params.update({"type": "invoice"})
        address_list = self.address_service.dispatch(
            "create", params=self.address_params
        )["data"]
        for address in address_list:
            if address["id"] not in address_ids:
                created_address = address
        self.assertIsNotNone(created_address)
        address = self.env["res.partner"].browse(created_address["id"])
        self.assertEqual(address.parent_id, self.partner)
        self.check_data(address, self.address_params)

    def test_update_address(self):
        params = dict(self.address_params, parent_id=self.partner.id)
        expected = dict(params)
        self._test_update_address(self.address.id, params, expected)
        params = dict(params, email="foo@baz.test", type="contact")
        # "contact" type get the address from the parent
        expected = dict(params, street=self.partner.street)
        self._test_update_address(self.address.id, params, expected)

    def test_read_address_profile(self):
        res = self.address_service.dispatch(
            "search", params={"scope": {"address_type": "profile"}}
        )["data"]
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["id"], self.partner.id)

    def test_read_address_address(self):
        res = self.address_service.dispatch(
            "search", params={"scope": {"address_type": "address"}}
        )["data"]
        self.assertEqual(len(res), 2)
        ids = {x["id"] for x in res}
        expected_ids = {self.address.id, self.address_2.id}
        self.assertEqual(ids, expected_ids)

    def test_read_address_invoice(self):
        # Create an invoice address
        # Search it
        self.address_params.update({"type": "invoice"})
        self.address_service.dispatch("create", params=self.address_params)[
            "data"
        ]
        res = self.address_service.dispatch(
            "search", params={"scope": {"type": "invoice"}}
        )["data"]
        self.assertEqual(len(res), 1)

    def test_read_address_all(self):
        res = self.address_service.dispatch("search", params={})["data"]
        self.assertEqual(len(res), 3)
        ids = {x["id"] for x in res}
        expected_ids = {self.partner.id, self.address.id, self.address_2.id}
        self.assertEqual(ids, expected_ids)

    def test_search_per_page(self):
        # Ensure the 'per_page' is working into search.
        res = self.address_service.dispatch("search", params={"per_page": 2})[
            "data"
        ]
        self.assertEqual(len(res), 2)
        # Ensure the 'page' is working. As there is 3 address for logged user, we
        # should have only 1 remaining result on the second page.
        res = self.address_service.dispatch(
            "search", params={"per_page": 2, "page": 2}
        )["data"]
        self.assertEqual(len(res), 1)

    def test_delete_address(self):
        address_id = self.address.id
        self.address_service.delete(address_id)
        address = self.env["res.partner"].search([("id", "=", address_id)])
        self.assertEqual(len(address), 0)
        partner = self.env["res.partner"].search(
            [("id", "=", self.partner.id)]
        )
        self.assertEqual(len(partner), 1)

    def test_delete_main_address(self):
        with self.assertRaises(AccessError):
            self.address_service.delete(self.partner.id)


class AddressCase(CommonAddressCase, AddressTestCase):
    """ Test address"""
