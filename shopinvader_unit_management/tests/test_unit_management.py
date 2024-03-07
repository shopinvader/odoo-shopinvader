# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import AccessError

from .common import TestUnitManagementCommon


class TestUnitManagement(TestUnitManagementCommon):
    def test_unit_management_units(self):
        self.assertEqual(self.unit_1.unit_profile, "unit")
        self.assertEqual(
            self.unit_1._get_unit_members(),
            self.manager_1_1
            | self.collaborator_1_1
            | self.collaborator_1_2
            | self.collaborator_1_3
            | self.collaborator_1_4
            | self.collaborator_1_5,
        )
        self.assertEqual(self.unit_1._get_unit_managers(), self.manager_1_1)
        self.assertEqual(
            self.unit_1._get_unit_collaborators(),
            self.collaborator_1_1
            | self.collaborator_1_2
            | self.collaborator_1_3
            | self.collaborator_1_4
            | self.collaborator_1_5,
        )
        with self.assertRaises(AccessError):
            self.unit_1._get_unit()

        self.assertEqual(self.unit_2.unit_profile, "unit")
        self.assertEqual(
            self.unit_2._get_unit_members(),
            self.manager_2_1
            | self.manager_2_2
            | self.collaborator_2_1
            | self.collaborator_2_2
            | self.collaborator_2_3,
        )
        self.assertEqual(
            self.unit_2._get_unit_managers(), self.manager_2_1 | self.manager_2_2
        )
        self.assertEqual(
            self.unit_2._get_unit_collaborators(),
            self.collaborator_2_1 | self.collaborator_2_2 | self.collaborator_2_3,
        )
        with self.assertRaises(AccessError):
            self.unit_2._get_unit()

        self.assertEqual(self.unit_3.unit_profile, "unit")
        self.assertEqual(
            self.unit_3._get_unit_members(),
            self.collaborator_3_1 | self.collaborator_3_2 | self.collaborator_3_3,
        )
        self.assertEqual(self.unit_3._get_unit_managers(), self.env["res.partner"])
        self.assertEqual(
            self.unit_3._get_unit_collaborators(),
            self.collaborator_3_1 | self.collaborator_3_2 | self.collaborator_3_3,
        )
        with self.assertRaises(AccessError):
            self.unit_3._get_unit()

        self.assertEqual(self.unit_4.unit_profile, "unit")
        self.assertEqual(
            self.unit_4._get_unit_members(), self.manager_4_1 | self.manager_4_2
        )
        self.assertEqual(
            self.unit_4._get_unit_managers(), self.manager_4_1 | self.manager_4_2
        )
        self.assertEqual(
            self.unit_4._get_unit_collaborators(),
            self.env["res.partner"],
        )
        with self.assertRaises(AccessError):
            self.unit_4._get_unit()

    def test_unit_management_managers(self):
        self.assertEqual(self.manager_1_1.unit_profile, "manager")
        self.assertEqual(self.manager_1_1._get_unit(), self.unit_1)

        with self.assertRaises(AccessError):
            self.manager_1_1._get_unit_members()
        with self.assertRaises(AccessError):
            self.manager_1_1._get_unit_managers()
        with self.assertRaises(AccessError):
            self.manager_1_1._get_unit_collaborators()

        self.assertEqual(self.manager_4_2.unit_profile, "manager")
        self.assertEqual(self.manager_4_2._get_unit(), self.unit_4)

        with self.assertRaises(AccessError):
            self.manager_4_2._get_unit_members()
        with self.assertRaises(AccessError):
            self.manager_4_2._get_unit_managers()
        with self.assertRaises(AccessError):
            self.manager_4_2._get_unit_collaborators()

    def test_unit_management_collaborators(self):
        self.assertEqual(self.collaborator_1_1.unit_profile, "collaborator")
        self.assertEqual(self.collaborator_1_1._get_unit(), self.unit_1)

        with self.assertRaises(AccessError):
            self.collaborator_1_1._get_unit_members()
        with self.assertRaises(AccessError):
            self.collaborator_1_1._get_unit_managers()
        with self.assertRaises(AccessError):
            self.collaborator_1_1._get_unit_collaborators()

        self.assertEqual(self.collaborator_3_3.unit_profile, "collaborator")
        self.assertEqual(self.collaborator_3_3._get_unit(), self.unit_3)

        with self.assertRaises(AccessError):
            self.collaborator_3_3._get_unit_members()
        with self.assertRaises(AccessError):
            self.collaborator_3_3._get_unit_managers()
        with self.assertRaises(AccessError):
            self.collaborator_3_3._get_unit_collaborators()
