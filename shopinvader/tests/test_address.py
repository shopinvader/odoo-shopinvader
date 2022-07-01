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

    def _create_address(self, params):
        existing_res = self.address_service.search(per_page=100)["data"]
        existing_ids = {address["id"] for address in existing_res}
        self.address_service.dispatch("create", params=params)["data"]
        after_res = self.address_service.search(per_page=100)["data"]
        after_ids = {address["id"] for address in after_res}
        created_ids = after_ids - existing_ids
        return self.env["res.partner"].browse(created_ids)

    def _test_create_address(self, params, expected):
        address = self._create_address(params)
        self.check_data(address, expected)
        return address

    def _test_update_address(self, address_id, params, expected):
        self.address_service.dispatch("update", address_id, params=params)
        address = self.env["res.partner"].browse(address_id)
        self.check_data(address, expected)
        return address

    def _test_search_address(self, params, expected):
        """Test search address with params and asserts results

        :param params: search parameters
        :param expected: res.partner recordset.
        """
        res = self.address_service.dispatch("search", params=params)["data"]
        res_ids = {x["id"] for x in res}
        records = self.env["res.partner"].browse(res_ids)
        self.assertEqual(records, expected)
        return records


class AddressTestCase(object):
    def test_create_address(self):
        # no email, verify defaults
        params = dict(self.address_params, type="other")
        self._test_create_address(params, params)
        # pass email and type
        params = dict(self.address_params, email="purple@test.oca", type="invoice")
        self._test_create_address(params, params)
        # pass country as code
        params = dict(self.address_params, country={"code": "FR"}, type="other")
        self._test_create_address(params, dict(self.address_params))
        # can't pass both country id and country code
        params = dict(params, country={"id": 1, "code": "FR"}, type="other")
        with self.assertRaisesRegex(UserError, r"'id' must not be present with 'code'"):
            self._test_create_address(params, dict(self.address_params))

    def test_add_address_invoice(self):
        # Create an invoice address with wrong type
        # Check raise
        params = dict(self.address_params, type="wrong")
        with self.assertRaises(UserError):
            self.address_service.dispatch("create", params=params)
        # Create an invoice address with invoice type
        params = dict(self.address_params, type="invoice")
        self._test_create_address(params, params)

    def test_update_address(self):
        # Case 1: Simply update fields (type is "other")
        params = dict(self.address_params)
        self._test_update_address(self.address.id, params, params)
        # Case 2: "contact" type get the address from the parent
        params = dict(self.address_params, email="foo@baz.test", type="contact")
        expected = dict(params, street=self.partner.street)
        self._test_update_address(self.address.id, params, expected)

    def test_read_address_profile(self):
        params = {"scope": {"address_type": "profile"}}
        expected = self.partner
        self._test_search_address(params, expected)

    def test_read_address_address(self):
        params = {"scope": {"address_type": "address"}}
        expected = self.address + self.address_2
        self._test_search_address(params, expected)

    def test_read_address_invoice(self):
        # Create an invoice address
        params = dict(self.address_params, type="invoice")
        address = self._create_address(params)
        # Search it
        params = {"scope": {"type": "invoice"}}
        self._test_search_address(params, address)

    def test_read_address_all(self):
        params = {}
        expected = self.partner + self.address + self.address_2
        self._test_search_address(params, expected)

    def test_search_per_page(self):
        # Ensure the 'per_page' is working into search.
        res = self.address_service.dispatch("search", params={"per_page": 2})["data"]
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
        partner = self.env["res.partner"].search([("id", "=", self.partner.id)])
        self.assertEqual(len(partner), 1)

    def test_delete_main_address(self):
        with self.assertRaises(AccessError):
            self.address_service.delete(self.partner.id)


class AddressCase(CommonAddressCase, AddressTestCase):
    """Test address"""
