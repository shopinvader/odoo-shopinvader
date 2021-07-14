# Copyright 2019 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import CommonCase


class TestCustomer(CommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.base_data = {
            "email": "acme@ltd.com",
            "name": "Purple",
            "street": "Rue du jardin",
            "zip": "43110",
            "city": "Aurec sur Loire",
            "phone": "0485485454",
            "country": {"id": cls.env.ref("base.fr").id},
            "is_company": False,
            "external_id": "12345678",
        }
        cls.partner = cls.env.ref("shopinvader.partner_1")

    def setUp(self):
        super().setUp()
        with self.work_on_services(partner=None) as work:
            self.customer_service = work.component(usage="customer")

    def address_service(self, **kw):
        with self.work_on_services(**kw) as work:
            return work.component(usage="addresses")

    def _find_activity(self, record):
        domain = [
            ("res_model_id", "=", self.env.ref("base.model_res_partner").id),
            ("res_id", "=", record.id),
            (
                "activity_type_id",
                "=",
                self.env.ref("shopinvader.mail_activity_review_customer").id,
            ),
        ]
        return self.env["mail.activity"].search_count(domain)

    def _create_customer(self, **kw):
        data = dict(self.base_data)
        data.update(kw)
        self.customer_service._reset_partner_work_context()
        self.customer_service.dispatch("create", params=data)["data"]
        return self.customer_service.partner

    def _create_address(self, partner=None, **kw):
        data = dict(self.base_data)
        data.update(kw)
        res = self.address_service(partner=partner or self.partner).dispatch(
            "create", params=data
        )["data"]
        new_address = [x for x in res if x["name"] == kw["name"]][0]
        return self.env["res.partner"].browse(new_address["id"])

    def _update_partner(self, partner, rec_id, **kw):
        self.address_service(partner=partner).dispatch("update", rec_id, params=kw)

    def test_notify_none(self):
        # set none
        self.backend.salesman_notify_create = ""
        self.backend.salesman_notify_update = ""
        # normal customer create -> none
        partner = self._create_customer()
        self.assertFalse(self._find_activity(partner))
        # normal customer update -> none
        self._update_partner(partner, partner.id, name="Pippo")
        self.assertFalse(self._find_activity(partner))
        # company create -> none
        partner = self._create_customer(
            external_id="12345678X",
            is_company=True,
            vat="BE0477472701",
            email="acme@foo.com",
        )
        self.assertFalse(self._find_activity(partner))
        # company update -> none
        self._update_partner(partner, partner.id, name="C2C")
        self.assertFalse(self._find_activity(partner))
        # address create -> none
        partner = self._create_address(name="John Doe")
        self.assertFalse(self._find_activity(partner.parent_id))
        # address update -> none
        self._update_partner(partner.parent_id, partner.id, name="Somewhere else")
        self.assertFalse(self._find_activity(partner.parent_id))

    def test_notify_company(self):
        self.backend.salesman_notify_create = "company"
        self.backend.salesman_notify_update = ""
        # normal customer create -> none
        partner = self._create_customer()
        self.assertFalse(self._find_activity(partner))
        # normal customer update -> none
        self._update_partner(partner, partner.id, name="Pippo")
        self.assertFalse(self._find_activity(partner))
        # company create -> yes
        partner = self._create_customer(
            external_id="12345678X",
            is_company=True,
            vat="BE0477472701",
            email="acme@foo.com",
        )
        self.assertEqual(self._find_activity(partner), 1)
        # company update -> none
        self._update_partner(partner, partner.id, name="C2C")
        self.assertEqual(self._find_activity(partner), 1)
        # enable for company update
        self.backend.salesman_notify_update = "company"
        # company update -> one more
        self._update_partner(partner, partner.id, name="C2C again")
        self.assertEqual(self._find_activity(partner), 2)
        # address create -> none
        partner = self._create_address(name="John Doe")
        self.assertFalse(self._find_activity(partner.parent_id))
        # address update -> none
        self._update_partner(partner.parent_id, partner.id, name="Somewhere else")
        self.assertFalse(self._find_activity(partner.parent_id))

    def test_notify_user(self):
        # set none
        self.backend.salesman_notify_create = "user"
        self.backend.salesman_notify_update = ""
        # normal customer create -> yes
        partner = self._create_customer()
        self.assertTrue(self._find_activity(partner))
        # normal customer update -> none
        self._update_partner(partner, partner.id, name="Pippo")
        self.assertEqual(self._find_activity(partner), 1)
        # enable for user update
        self.backend.salesman_notify_update = "user"
        # normal customer update -> yes
        self._update_partner(partner, partner.id, name="Pippo")
        self.assertEqual(self._find_activity(partner), 2)
        # company
        partner = self._create_customer(
            external_id="12345678X",
            is_company=True,
            vat="BE0477472701",
            email="acme@foo.com",
        )
        self.assertFalse(self._find_activity(partner))
        # company update -> none
        self._update_partner(partner, partner.id, name="C2C")
        self.assertFalse(self._find_activity(partner))
        # address create -> none
        partner = self._create_address(name="John Doe")
        self.assertFalse(self._find_activity(partner.parent_id))
        # address update -> none
        self._update_partner(partner.parent_id, partner.id, name="Somewhere else")
        self.assertFalse(self._find_activity(partner.parent_id))

    def test_notify_company_and_user(self):
        # set none
        self.backend.salesman_notify_create = "company_and_user"
        self.backend.salesman_notify_update = ""
        # normal customer create -> yes
        partner = self._create_customer()
        self.assertTrue(self._find_activity(partner))
        # normal customer update -> none
        self._update_partner(partner, partner.id, name="Pippo")
        self.assertEqual(self._find_activity(partner), 1)
        # enable for user update
        self.backend.salesman_notify_update = "company_and_user"
        # company create -> yes
        partner = self._create_customer(
            external_id="12345678X",
            is_company=True,
            vat="BE0477472701",
            email="acme@foo.com",
        )
        self.assertEqual(self._find_activity(partner), 1)
        # company update -> none
        self.backend.salesman_notify_update = ""
        self._update_partner(partner, partner.id, name="C2C")
        self.assertEqual(self._find_activity(partner), 1)
        # enable for company update
        self.backend.salesman_notify_update = "company_and_user"
        # company update -> one more
        self._update_partner(partner, partner.id, name="C2C again")
        self.assertEqual(self._find_activity(partner), 2)
        # address create -> none
        partner = self._create_address(name="John Doe")
        self.assertFalse(self._find_activity(partner.parent_id))
        # address update -> none
        self._update_partner(partner.parent_id, partner.id, name="Somewhere else")
        self.assertFalse(self._find_activity(partner.parent_id))

    def test_notify_address(self):
        # set none
        self.backend.salesman_notify_create = "address"
        self.backend.salesman_notify_update = "address"
        # normal customer create -> none
        partner = self._create_customer()
        self.assertFalse(self._find_activity(partner))
        # normal customer update -> none
        self._update_partner(partner, partner.id, name="Pippo")
        self.assertFalse(self._find_activity(partner))
        # company create -> none
        partner = self._create_customer(
            external_id="12345678X",
            is_company=True,
            vat="BE0477472701",
            email="acme@foo.com",
        )
        self.assertFalse(self._find_activity(partner))
        # company update -> none
        self._update_partner(partner, partner.id, name="C2C")
        self.assertFalse(self._find_activity(partner))
        # address create -> yes
        partner = self._create_address(name="John Doe")
        self.assertEqual(self._find_activity(partner.parent_id), 1)
        # address update -> yes
        self._update_partner(partner.parent_id, partner.id, name="Pippo")
        self.assertEqual(self._find_activity(partner.parent_id), 2)
