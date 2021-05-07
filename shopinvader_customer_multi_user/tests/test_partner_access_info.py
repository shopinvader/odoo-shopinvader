# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from .common import TestUserManagementCommmon


class TestPartnerAccessInfo(TestUserManagementCommmon):
    def _get_access_info(self, **params):
        _params = dict(
            partner=self.company_binding.record_id,
            partner_user=self.company_binding.record_id,
            invader_partner=self.company_binding,
            invader_partner_user=self.company_binding,
        )
        _params.update(params)
        with self.backend.work_on("res.partner") as work:
            comp = work.component(usage="access.info")
            self._update_work_ctx(comp, **_params)
            return comp

    def test_access_info_admin(self):
        info = self._get_access_info().permissions()
        self.assertTrue(info["users"]["manage"])

    def test_access_info_simpleuser(self):
        for binding in (
            self.user_binding + self.user_binding2 + self.user_binding3
        ):
            info = self._get_access_info(
                partner_user=binding.record_id, invader_partner_user=binding,
            ).permissions()
            self.assertFalse(info["users"]["manage"])

    def test_access_info_simpleuser_delegated(self):
        binding = self.user_binding
        binding.can_manage_users = True
        info = self._get_access_info(
            partner_user=binding.record_id, invader_partner_user=binding,
        ).permissions()
        self.assertTrue(info["users"]["manage"])

    def test_access_info_address_admin(self):
        """Admin can always CRUD addresses."""
        for binding in (
            self.user_binding + self.user_binding2 + self.user_binding3
        ):
            info = self._get_access_info().for_address(binding.record_id)
            expected = {"read": True, "update": True, "delete": True}
            self.assertEqual(info, expected)

    def test_access_info_address_simpleuser_owner(self):
        """Owners can always CRUD their addresses."""
        for binding in (
            self.user_binding + self.user_binding2 + self.user_binding3
        ):
            info = self._get_access_info(
                partner_user=binding.record_id, invader_partner_user=binding,
            ).for_address(binding.record_id.id)
            # They can edit their own record
            expected = {"read": True, "update": True, "delete": True}
            self.assertEqual(info, expected)

    def test_access_info_address_simpleuser_not_owner(self):
        """Owners can only READ others' addresses."""
        binding = self.user_binding
        access_info = self._get_access_info(
            partner_user=binding.record_id, invader_partner_user=binding,
        )
        for binding in self.user_binding2 + self.user_binding3:
            info = access_info.for_address(binding.record_id.id)
            expected = {"read": True, "update": False, "delete": False}
            self.assertEqual(info, expected)

        binding = self.user_binding2
        access_info = self._get_access_info(
            partner_user=binding.record_id, invader_partner_user=binding,
        )
        for binding in self.user_binding + self.user_binding3:
            info = access_info.for_address(binding.record_id.id)
            expected = {"read": True, "update": False, "delete": False}
            self.assertEqual(info, expected)

        binding = self.user_binding3
        access_info = self._get_access_info(
            partner_user=binding.record_id, invader_partner_user=binding,
        )
        for binding in self.user_binding + self.user_binding2:
            info = access_info.for_address(binding.record_id.id)
            expected = {"read": True, "update": False, "delete": False}
            self.assertEqual(info, expected)
