# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from .common import TestUnitManagementCommon


class TestUnitManagement(TestUnitManagementCommon):
    def test_unit_management_units(self):
        self.assertEqual(self.unit_1.unit_profile, "unit")
        self.assertEqual(
            self.unit_1.member_ids,
            self.manager_1_1
            | self.collaborator_1_1
            | self.collaborator_1_2
            | self.collaborator_1_3
            | self.collaborator_1_4
            | self.collaborator_1_5,
        )
        self.assertEqual(self.unit_1.manager_ids, self.manager_1_1)
        self.assertEqual(
            self.unit_1.collaborator_ids,
            self.collaborator_1_1
            | self.collaborator_1_2
            | self.collaborator_1_3
            | self.collaborator_1_4
            | self.collaborator_1_5,
        )
        self.assertFalse(self.unit_1.unit_id)

        self.assertEqual(self.unit_2.unit_profile, "unit")
        self.assertEqual(
            self.unit_2.member_ids,
            self.manager_2_1
            | self.manager_2_2
            | self.collaborator_2_1
            | self.collaborator_2_2
            | self.collaborator_2_3,
        )
        self.assertEqual(self.unit_2.manager_ids, self.manager_2_1 | self.manager_2_2)
        self.assertEqual(
            self.unit_2.collaborator_ids,
            self.collaborator_2_1 | self.collaborator_2_2 | self.collaborator_2_3,
        )
        self.assertFalse(self.unit_2.unit_id)

        self.assertEqual(self.unit_3.unit_profile, "unit")
        self.assertEqual(
            self.unit_3.member_ids,
            self.collaborator_3_1 | self.collaborator_3_2 | self.collaborator_3_3,
        )
        self.assertEqual(self.unit_3.manager_ids, self.env["res.partner"])
        self.assertEqual(
            self.unit_3.collaborator_ids,
            self.collaborator_3_1 | self.collaborator_3_2 | self.collaborator_3_3,
        )
        self.assertFalse(self.unit_3.unit_id)

        self.assertEqual(self.unit_4.unit_profile, "unit")
        self.assertEqual(self.unit_4.member_ids, self.manager_4_1 | self.manager_4_2)
        self.assertEqual(self.unit_4.manager_ids, self.manager_4_1 | self.manager_4_2)
        self.assertEqual(
            self.unit_4.collaborator_ids,
            self.env["res.partner"],
        )
        self.assertFalse(self.unit_4.unit_id)

    def test_unit_management_managers(self):
        self.assertEqual(self.manager_1_1.unit_profile, "manager")
        self.assertEqual(self.manager_1_1.unit_id, self.unit_1)

        self.assertFalse(self.manager_1_1.member_ids)
        self.assertFalse(self.manager_1_1.manager_ids)
        self.assertFalse(self.manager_1_1.collaborator_ids)

        self.assertEqual(self.manager_4_2.unit_profile, "manager")
        self.assertEqual(self.manager_4_2.unit_id, self.unit_4)

        self.assertFalse(self.manager_4_2.member_ids)
        self.assertFalse(self.manager_4_2.manager_ids)
        self.assertFalse(self.manager_4_2.collaborator_ids)

    def test_unit_management_collaborators(self):
        self.assertEqual(self.collaborator_1_1.unit_profile, "collaborator")
        self.assertEqual(self.collaborator_1_1.unit_id, self.unit_1)

        self.assertFalse(self.collaborator_1_1.member_ids)
        self.assertFalse(self.collaborator_1_1.manager_ids)
        self.assertFalse(self.collaborator_1_1.collaborator_ids)

        self.assertEqual(self.collaborator_3_3.unit_profile, "collaborator")
        self.assertEqual(self.collaborator_3_3.unit_id, self.unit_3)

        self.assertFalse(self.collaborator_3_3.member_ids)
        self.assertFalse(self.collaborator_3_3.manager_ids)
        self.assertFalse(self.collaborator_3_3.collaborator_ids)
