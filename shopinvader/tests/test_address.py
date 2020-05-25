# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import AccessError

from .common import CommonCase


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

    def check_data(cls, address, data):
        for key in data:
            if key == "partner_email":
                continue
            elif key == "country":
                cls.assertEqual(address.country_id.id, data[key]["id"])
            else:
                cls.assertEqual(address[key], data[key])


class AddressTestCase(object):
    def test_add_address(self):
        address_ids = [
            address["id"] for address in self.address_service.search()["data"]
        ]
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
        params = self.address_params
        self.address_service.dispatch("update", self.address.id, params=params)
        self.assertEqual(self.address.parent_id, self.partner)
        self.check_data(self.address, params)

    # TODO MIGRATE
    #    def test_update_main_address(self):
    #        params = self.address_params
    #        params['id'] = self.partner.id
    #        self.address_service.update(params)
    #        self.check_data(self.partner, params)
    #

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
