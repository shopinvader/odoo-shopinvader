# Copyright 2026 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import AccessDenied, MissingError

from .common import CommonFastAPIEndpointCase


class RouterHelperCase(CommonFastAPIEndpointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.partner_category_1 = cls.env["res.partner.category"].create(
            {"name": "category_1"}
        )
        cls.partner_category_2 = cls.env["res.partner.category"].create(
            {"name": "category_2"}
        )
        cls.partner_1_1 = cls.env["res.partner"].create(
            {
                "name": "Partner 1 1",
                "category_id": [(6, 0, [cls.partner_category_1.id])],
                "color": 1,
            }
        )
        cls.partner_1_2 = cls.env["res.partner"].create(
            {
                "name": "Partner 1 2",
                "category_id": [(6, 0, [cls.partner_category_1.id])],
                "color": 2,
            }
        )
        cls.partner_2_1 = cls.env["res.partner"].create(
            {
                "name": "Partner 2 1",
                "category_id": [(6, 0, [cls.partner_category_2.id])],
                "color": 3,
            }
        )

    def test_base_init(self):
        helper = self.env["shopinvader.router.base_test.helper"].new({})
        self.assertNotEqual(helper.id, None)
        self.assertEqual(helper.id.__class__.__name__, "NewId")

    def test_base_param(self):
        helper = self.env["shopinvader.router.base_test.helper"].new(
            {
                "name": "Test",
                "type": "type_2",
            }
        )
        self.assertEqual(helper.name, "Test")
        self.assertEqual(helper.type, "type_2")

    def test_base_param_default(self):
        helper = self.env["shopinvader.router.base_test.helper"].new({})
        self.assertFalse(helper.name)
        self.assertEqual(helper.type, "type_1")

    def test_base_no_model_get(self):
        helper = self.env["shopinvader.router.base_test.helper"].new({})
        with self.assertRaises(NotImplementedError):
            helper.get(1)

    def test_base_no_model_search(self):
        helper = self.env["shopinvader.router.base_test.helper"].new({})
        with self.assertRaises(NotImplementedError):
            helper.search([])

    def test_base_no_model_search_with_count(self):
        helper = self.env["shopinvader.router.base_test.helper"].new({})
        with self.assertRaises(NotImplementedError):
            helper.search_with_count([])

    def test_base_no_model_domain(self):
        helper = self.env["shopinvader.router.no_domain_test.helper"].new({})
        with self.assertRaises(NotImplementedError):
            helper.search([])

    def test_relations(self):
        helper = self.env["shopinvader.router.relations_test.helper"].new(
            {"partner_id": self.partner_1_1.id}
        )
        self.assertEqual(helper.partner_id, self.partner_1_1)
        self.assertEqual(helper.partner_name, "Partner 1 1")

    def test_values_resilience_flush_recordset(self):
        helper = self.env["shopinvader.router.relations_test.helper"].new(
            {"name": "Test", "partner_id": self.partner_1_1.id}
        )

        helper.flush_recordset()
        self.assertEqual(helper.name, "Test")
        self.assertEqual(helper.partner_id, self.partner_1_1)
        self.assertEqual(helper.partner_name, "Partner 1 1")

    def test_values_resilience_flush_model(self):
        helper = self.env["shopinvader.router.relations_test.helper"].new(
            {"name": "Test", "partner_id": self.partner_1_1.id}
        )

        helper.flush_model()
        self.assertEqual(helper.name, "Test")
        self.assertEqual(helper.partner_id, self.partner_1_1)
        self.assertEqual(helper.partner_name, "Partner 1 1")

    def test_values_resilience_flush_cr(self):
        helper = self.env["shopinvader.router.relations_test.helper"].new(
            {"name": "Test", "partner_id": self.partner_1_1.id}
        )
        helper.env.cr.flush()
        self.assertEqual(helper.name, "Test")
        self.assertEqual(helper.partner_id, self.partner_1_1)
        self.assertEqual(helper.partner_name, "Partner 1 1")

    def test_values_resilience_invalidate_all(self):
        # /!\ Invalidating cache loses all data for the helpers:
        helper = self.env["shopinvader.router.relations_test.helper"].new(
            {"name": "Test", "partner_id": self.partner_1_1.id}
        )
        helper.env.invalidate_all()
        self.assertEqual(helper.name, "Test")
        self.assertEqual(helper.partner_id, self.partner_1_1)
        self.assertEqual(helper.partner_name, "Partner 1 1")

    def test_values_resilience_cursor_clear(self):
        # /!\ Clearing cache loses all data for the helpers:
        helper = self.env["shopinvader.router.relations_test.helper"].new(
            {"name": "Test", "partner_id": self.partner_1_1.id}
        )
        helper.env.cr.clear()
        self.assertEqual(helper.name, "Test")
        self.assertEqual(helper.partner_id, self.partner_1_1)
        self.assertEqual(helper.partner_name, "Partner 1 1")

    def test_model_bound_read_1(self):
        helper = self.env["shopinvader.router.model_bound_test.helper"].new(
            {"category_ids": [(6, 0, [self.partner_category_1.id])]}
        )
        self.assertEqual(helper.category_ids.ids, self.partner_category_1.ids)
        self.assertEqual(helper.search(), self.partner_1_1 | self.partner_1_2)
        self.assertEqual(
            helper.search_with_count(), (2, self.partner_1_1 | self.partner_1_2)
        )
        self.assertEqual(helper.search_with_count(limit=1), (2, self.partner_1_1))
        self.assertEqual(helper.get(self.partner_1_1.id), self.partner_1_1)
        self.assertEqual(helper.get(self.partner_1_2.id), self.partner_1_2)

        self.assertEqual(helper.search([("color", "=", 1)]), self.partner_1_1)
        self.assertEqual(
            helper.search_with_count([("color", "=", 2)]),
            (1, self.partner_1_2),
        )

        with self.assertRaises(MissingError):
            helper.get(self.partner_2_1.id)

    def test_model_bound_read_2(self):
        helper = self.env["shopinvader.router.model_bound_test.helper"].new(
            {"category_ids": [(6, 0, [self.partner_category_2.id])]}
        )
        self.assertEqual(helper.category_ids.ids, self.partner_category_2.ids)
        self.assertEqual(helper.search(), self.partner_2_1)
        self.assertEqual(helper.search_with_count(), (1, self.partner_2_1))
        self.assertEqual(helper.search_with_count(limit=1), (1, self.partner_2_1))
        self.assertEqual(helper.get(self.partner_2_1.id), self.partner_2_1)

        self.assertEqual(helper.search([("color", "=", 1)]), self.env["res.partner"])
        self.assertEqual(
            helper.search_with_count([("color", "=", 1)]), (0, self.env["res.partner"])
        )
        self.assertEqual(helper.search([("color", "=", 3)]), self.partner_2_1)

        with self.assertRaises(MissingError):
            helper.get(self.partner_1_1.id)

    def test_model_bound_create(self):
        helper = self.env["shopinvader.router.model_bound_test.helper"].new(
            {"category_ids": [(6, 0, [self.partner_category_1.id])]}
        )
        partner = helper.create(
            {
                "name": "New Partner",
                "category_id": [(6, 0, [self.partner_category_1.id])],
                "color": 1,
            }
        )
        self.assertEqual(helper.get(partner.id), partner)

    def test_model_bound_outside_create(self):
        helper = self.env["shopinvader.router.model_bound_test.helper"].new(
            {"category_ids": [(6, 0, [self.partner_category_1.id])]}
        )
        with self.assertRaises(AccessDenied):
            helper.create(
                {
                    "name": "New Partner",
                    "category_id": [(6, 0, [self.partner_category_2.id])],
                    "color": 1,
                }
            )

    def test_model_bound_write(self):
        helper = self.env["shopinvader.router.model_bound_test.helper"].new(
            {"category_ids": [(6, 0, [self.partner_category_1.id])]}
        )
        helper.write(
            self.partner_1_1.id,
            {
                "name": "Partner eleven",
                "color": 12,
            },
        )
        self.assertEqual(helper.get(self.partner_1_1.id).name, "Partner eleven")
        self.assertEqual(helper.get(self.partner_1_1.id).color, 12)

    def test_model_bound_outside_write(self):
        helper = self.env["shopinvader.router.model_bound_test.helper"].new(
            {"category_ids": [(6, 0, [self.partner_category_1.id])]}
        )
        with self.assertRaises(MissingError):
            helper.write(
                self.partner_2_1.id,
                {
                    "name": "Partner twenty one",
                    "color": 12,
                },
            )

    def test_model_bound_inside_out_write(self):
        helper = self.env["shopinvader.router.model_bound_test.helper"].new(
            {"category_ids": [(6, 0, [self.partner_category_1.id])]}
        )
        with self.assertRaises(AccessDenied):
            helper.write(
                self.partner_1_1.id,
                {
                    "category_id": [(6, 0, [self.partner_category_2.id])],
                },
            )

    def test_model_bound_unlink(self):
        helper = self.env["shopinvader.router.model_bound_test.helper"].new(
            {"category_ids": [(6, 0, [self.partner_category_1.id])]}
        )
        helper.unlink(self.partner_1_1.id)
        with self.assertRaises(MissingError):
            self.assertFalse(helper.get(self.partner_1_1.id))

    def test_model_bound_outside_unlink(self):
        helper = self.env["shopinvader.router.model_bound_test.helper"].new(
            {"category_ids": [(6, 0, [self.partner_category_1.id])]}
        )
        with self.assertRaises(MissingError):
            helper.unlink(self.partner_2_1.id)

    def test_model_bound_rv_unlink(self):
        helper = self.env["shopinvader.router.model_bound_test.helper"].new(
            {"category_ids": [(6, 0, [self.partner_category_1.id])]}
        )
        name = helper.unlink(self.partner_1_1.id, lambda r: r.name)
        with self.assertRaises(MissingError):
            self.assertFalse(helper.get(self.partner_1_1.id))
        self.assertEqual(name, "Partner 1 1")
