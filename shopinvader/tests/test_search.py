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
        res = self.address_service.dispatch("search", params={"scope": scope})["data"]
        found = [(x["id"], x["name"]) for x in res]
        expected = [(x["id"], x["name"]) for x in self.address + self.address_2]
        self.assertEqual(found, expected)

        scope = {"name.ilike": "test%"}
        res = self.address_service.dispatch("search", params={"scope": scope})["data"]
        found = [(x["id"], x["name"]) for x in res]
        expected = [(x["id"], x["name"]) for x in self.address + self.address_2]
        self.assertEqual(found, expected)

        scope = {"name.ilike": "%whatever"}
        res = self.address_service.dispatch("search", params={"scope": scope})["data"]
        found = [(x["id"], x["name"]) for x in res]
        expected = [(x["id"], x["name"]) for x in self.address_2]
        self.assertEqual(found, expected)

    def test_search_bad_scope(self):
        scope = {"name.noway": "TEST%"}
        msg = "Invalid scope"
        with self.assertRaisesRegex(UserError, msg):
            self.address_service.dispatch("search", params={"scope": scope})

    def test_search_many2one(self):
        scope = {"country_id": self.env.ref("base.us").id}
        res = self.address_service.dispatch("search", params={"scope": scope})["data"]
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["id"], self.address_2.id)

    def test_search_many2one_from_url(self):
        # See https://github.com/OCA/rest-framework/blob/bbc8a1f26d59eef75507da1a0ce4ca31a261c70d/base_rest/http.py#L148-L152 # noqa
        import pyquerystring  # base_rest dependency

        params = pyquerystring.parse(
            "scope[country_id]=%d" % self.env.ref("base.us").id
        )
        res = self.address_service.dispatch("search", params=params)["data"]
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["id"], self.address_2.id)
