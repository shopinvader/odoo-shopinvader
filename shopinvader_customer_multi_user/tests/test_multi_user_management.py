# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import exceptions

from .common import TestUserManagementCommmon


class TestUserManagement(TestUserManagementCommmon):
    def test_search_as_admin(self):
        service = self._get_service(self.company)
        expected = self.user_binding2 + self.user_binding3 + self.user_binding
        self._test_search(service, expected)

    def test_search_as_simpleuser(self):
        for binding in (
            self.user_binding,
            self.user_binding2,
            self.user_binding3,
        ):
            service = self._get_service(binding.record_id)
            with self.assertRaisesRegex(exceptions.AccessError, "User not allowed"):
                service.dispatch("search")

    def test_create_as_admin(self):
        service = self._get_service(self.company)
        params = {
            "name": "John Doe",
            "email": "jdoe@test.com",
        }
        self._test_create(service, params)

    def test_create_as_simpleuser(self):
        for binding in (
            self.user_binding,
            self.user_binding2,
            self.user_binding3,
        ):
            service = self._get_service(binding.record_id)
            params = {
                "name": "Created by " + binding.name,
                "email": "created_by_" + binding.email,
            }
            with self.assertRaisesRegex(exceptions.AccessError, "User not allowed"):
                service.dispatch("create", params=params)

    def test_update_as_admin(self):
        service = self._get_service(self.company)
        params = {
            "name": self.user_binding.name + " UPDATED",
        }
        service.dispatch("update", self.user_binding.id, params=params)["data"]
        partner = self.company.child_ids.filtered_domain(
            [("email", "=", self.user_binding.email)]
        )
        self.assertEqual(partner.name, "Simple user UPDATED")

    def test_update_as_simpleuser(self):
        for binding in (
            self.user_binding,
            self.user_binding2,
            self.user_binding3,
        ):
            service = self._get_service(binding.record_id)
            params = {
                "name": self.user_binding.name + " UPDATED",
            }
            with self.assertRaisesRegex(exceptions.AccessError, "User not allowed"):
                service.dispatch("update", self.user_binding.id, params)

    def test_delete_as_admin(self):
        service = self._get_service(self.company)
        child_partner2 = self.user_binding2.record_id
        # Delete its user
        service.dispatch("delete", self.user_binding2.id)
        # The binding is gone
        self.assertFalse(self.user_binding2.exists())
        # BUT since its partner had another user it won't be touched
        self.assertTrue(child_partner2.active)
        # Let's delete the other user
        child_partner3 = self.user_binding3.record_id
        service.dispatch("delete", self.user_binding3.id)
        self.assertFalse(self.user_binding3.exists())
        # Now its partner is archived
        self.assertFalse(child_partner3.active)

    def test_delete_as_simpleuser(self):
        for binding in (
            self.user_binding,
            self.user_binding2,
            self.user_binding3,
        ):
            service = self._get_service(binding.record_id)
            with self.assertRaisesRegex(exceptions.AccessError, "User not allowed"):
                service.dispatch("delete", self.user_binding2.id)


class TestUserManagementDelegateManage(TestUserManagementCommmon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_binding.can_manage_users = True
        cls.user_binding2.can_manage_users = True

    # Test delegated permission: manage users

    def test_search_as_simpleuser_delegate_manage_users(self):
        # This user has no sub users, no result
        binding = self.user_binding
        service = self._get_service(binding.record_id)
        expected = self.user_binding2.browse()
        self._test_search(service, expected)

        # This user has a sub user, should find it
        binding = self.user_binding2
        service = self._get_service(binding.record_id)
        expected = self.user_binding3
        self._test_search(service, expected)

    def test_create_as_simpleuser_delegate_manage_users(self):
        binding = self.user_binding
        self.assertFalse(binding.child_ids)
        service = self._get_service(binding.record_id)
        params = {
            "name": "Created by " + binding.name,
            "email": "created_by_" + binding.email,
        }
        new_user = self._test_create(service, params)
        service.dispatch("delete", new_user.id)
        self.assertFalse(new_user.exists())

    def test_delete_as_simpleuser_delegate_manage_users(self):
        binding = self.user_binding
        service = self._get_service(binding.record_id)
        child_partner2 = self.user_binding2.record_id
        # Delete a user that does not belong to him
        with self.assertRaises(exceptions.MissingError):
            service.dispatch("delete", self.user_binding2.id)

        # Try to delete its sub user instead
        binding = self.user_binding2
        service = self._get_service(binding.record_id)
        child_partner3 = self.user_binding3.record_id
        service.dispatch("delete", self.user_binding3.id)
        self.assertFalse(self.user_binding3.exists())
        # BUT since its partner had another user it won't be touched
        self.assertTrue(child_partner2.active)
        self.assertFalse(child_partner3.active)
