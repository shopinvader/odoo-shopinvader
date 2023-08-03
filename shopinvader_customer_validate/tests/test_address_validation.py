# Copyright 2022 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import exceptions

from odoo.addons.shopinvader_v1_base.tests.common import CommonCase


class AddressValidationTestCase(CommonCase):
    def _create_customer(self, **kw):
        data = {
            "email": "new@customer.example.com",
            "external_id": "D5CdkqOEL",
            "name": "New Purple",
            "backend_id": self.backend.id,
        }
        data.update(kw)
        model = self.env["shopinvader.partner"]
        return model.create(data)

    def _create_address(self, **kw):
        data = {
            "name": "New Address",
        }
        data.update(kw)
        model = self.env["res.partner"]
        return model.create(data)

    def test_wiz_setup_1_backend(self):
        customer = self._create_customer()
        address = self._create_address(parent_id=customer.record_id.id)
        customer2 = self._create_customer(email="foo@bar.com")
        address2 = self._create_address(parent_id=customer2.record_id.id)
        addresses = address + address2
        wiz = addresses._get_shopinvader_validate_address_wizard()
        # 2 customers, only one backend -> all good
        self.assertRecordValues(
            wiz,
            [
                {
                    "backend_id": self.backend.id,
                    "valid_backend_ids": self.backend.ids,
                    "display_warning": False,
                    "next_state": "active",
                    "partner_ids": addresses.ids,
                }
            ],
        )

    def test_wiz_setup_1_backend_nested_hierarchy(self):
        customer = self._create_customer()
        address = self._create_address(parent_id=customer.record_id.id)
        customer2 = self._create_customer(email="foo@bar.com")
        address2 = self._create_address(parent_id=customer2.record_id.id)
        addresses = address + address2
        wiz = addresses._get_shopinvader_validate_address_wizard()
        # 2 customers, only one backend -> all good
        self.assertRecordValues(
            wiz,
            [
                {
                    "backend_id": self.backend.id,
                    "valid_backend_ids": self.backend.ids,
                    "display_warning": False,
                    "next_state": "active",
                    "partner_ids": addresses.ids,
                }
            ],
        )

    def test_wiz_setup_many_backends(self):
        customer = self._create_customer()
        address = self._create_address(parent_id=customer.record_id.id)
        b2 = self.backend.copy({"name": "B2", "tech_name": "b2"})
        customer2 = self._create_customer(backend_id=b2.id, email="foo@baz.com")
        address2 = self._create_address(parent_id=customer2.record_id.id)
        b3 = self.backend.copy({"name": "B3", "tech_name": "b3"})
        customer3 = self._create_customer(backend_id=b3.id, email="baz@foo.com")
        address3 = self._create_address(parent_id=customer3.record_id.id)
        backends = self.backend + b2 + b3
        addresses = address + address2 + address3
        wiz = addresses._get_shopinvader_validate_address_wizard()
        self.assertEqual(wiz.display_warning, True)
        self.assertEqual(wiz.valid_backend_ids, backends)
        with self.assertRaisesRegex(exceptions.UserError, "You must select a backend"):
            wiz.action_apply()

    def test_wiz_setup_2_backend_nested_hierarchy(self):
        customer = self._create_customer()
        parent = customer.record_id
        child_0_l1 = self._create_address(parent_id=parent.id)
        child_0_l2 = self._create_address(parent_id=child_0_l1.id)
        customer2 = self._create_customer(email="foo@baz.com")
        parent2 = customer2.record_id
        child_1_l1 = self._create_address(parent_id=parent2.id)
        child_1_l2 = self._create_address(parent_id=child_1_l1.id)
        addresses = child_0_l2 + child_1_l2
        wiz = addresses._get_shopinvader_validate_address_wizard()
        # 2 customers, only one backend -> all good
        self.assertRecordValues(
            wiz,
            [
                {
                    "backend_id": self.backend.id,
                    "valid_backend_ids": self.backend.ids,
                    "display_warning": False,
                    "next_state": "active",
                    "partner_ids": addresses.ids,
                }
            ],
        )

    def test_wiz_setup_many_backend_nested_hierarchy(self):
        customer = self._create_customer()
        parent = customer.record_id
        child_0_l1 = self._create_address(parent_id=parent.id)
        child_0_l2 = self._create_address(parent_id=child_0_l1.id)
        b2 = self.backend.copy({"name": "B2", "tech_name": "b2"})
        customer2 = self._create_customer(backend_id=b2.id, email="foo@baz.com")
        parent2 = customer2.record_id
        child_1_l1 = self._create_address(parent_id=parent2.id)
        child_1_l2 = self._create_address(parent_id=child_1_l1.id)
        backends = self.backend + b2
        addresses = child_0_l2 + child_1_l2
        wiz = addresses._get_shopinvader_validate_address_wizard()
        self.assertEqual(wiz.display_warning, True)
        self.assertEqual(wiz.valid_backend_ids, backends)
        with self.assertRaisesRegex(exceptions.UserError, "You must select a backend"):
            wiz.action_apply()
