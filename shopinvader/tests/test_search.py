# Copyright 2021 Camptocamp SA (http://www.camptocamp.com)
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError

from .common import CommonCase


class CommonSearchCase(CommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env.ref("shopinvader.partner_1")
        cls.address = cls.env.ref("shopinvader.partner_1_address_1")
        cls.address_2 = cls.env.ref("shopinvader.partner_1_address_2")

    def setUp(self):
        super().setUp()
        with self.work_on_services(partner=self.partner) as work:
            self.address_service = work.component(usage="addresses")


class SearchCase(CommonSearchCase):
    def test_domain_conversion(self):
        service = self.address_service
        scope = {
            "foo.gt": 1,
            "bar.gte": 2,
            "baz.lt": 3,
            "boo.lte": 4,
            "yoo.like": "Me%",
            "woo.ilike": "%you%",
        }
        expected = [
            ("foo", ">", 1),
            ("bar", ">=", 2),
            ("baz", "<", 3),
            ("boo", "<=", 4),
            ("yoo", "like", "Me%"),
            ("woo", "ilike", "%you%"),
        ]
        domain = service._scope_to_domain(scope)
        self.assertEqual(sorted(domain), sorted(expected))

    def test_search_by_text(self):
        self.address.name = "TEST ADDR 1"
        self.address_2.name = "TEST ADDR 2 WHATEVER"
        scope = {"name.like": "TEST%"}
        res = self.address_service.dispatch("search", params={"scope": scope})[
            "data"
        ]
        found = [(x["id"], x["name"]) for x in res]
        expected = [
            (x["id"], x["name"]) for x in self.address + self.address_2
        ]
        self.assertEqual(found, expected)

        scope = {"name.ilike": "test%"}
        res = self.address_service.dispatch("search", params={"scope": scope})[
            "data"
        ]
        found = [(x["id"], x["name"]) for x in res]
        expected = [
            (x["id"], x["name"]) for x in self.address + self.address_2
        ]
        self.assertEqual(found, expected)

        scope = {"name.ilike": "%whatever"}
        res = self.address_service.dispatch("search", params={"scope": scope})[
            "data"
        ]
        found = [(x["id"], x["name"]) for x in res]
        expected = [(x["id"], x["name"]) for x in self.address_2]
        self.assertEqual(found, expected)

    def test_search_bad_scope(self):
        scope = {"name.noway": "TEST%"}
        msg = "Invalid scope"
        with self.assertRaisesRegex(UserError, msg):
            self.address_service.dispatch("search", params={"scope": scope})
