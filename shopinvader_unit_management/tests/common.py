# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestUnitManagementCommon(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Set up demo data:
        managers = [1, 2, 0, 2]
        collaborators = [5, 3, 3, 0]
        for unit in range(1, 5):
            setattr(
                cls,
                f"unit_{unit}",
                cls.env.ref(f"shopinvader_unit_management.unit_{unit}"),
            )
            for manager in range(1, 1 + managers[unit - 1]):
                setattr(
                    cls,
                    f"manager_{unit}_{manager}",
                    cls.env.ref(
                        f"shopinvader_unit_management.unit_{unit}_manager_{manager}"
                    ),
                )
            for collaborator in range(1, 1 + collaborators[unit - 1]):
                setattr(
                    cls,
                    f"collaborator_{unit}_{collaborator}",
                    cls.env.ref(
                        f"shopinvader_unit_management.unit_{unit}_collaborator_{collaborator}"
                    ),
                )
