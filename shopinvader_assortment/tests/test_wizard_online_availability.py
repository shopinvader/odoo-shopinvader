# © 2022 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from odoo.exceptions import UserError
from odoo.tests.common import SavepointCase


class TestWizardOnlineAvailable(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.product1 = cls.env.ref("product.product_product_8")
        cls.product2 = cls.env.ref("product.product_product_7")
        cls.product3 = cls.env.ref("product.product_product_9")
        cls.product4 = cls.env.ref("product.product_product_24")
        cls.product5 = cls.env.ref("product.product_product_10")
        cls.product6 = cls.env.ref("product.product_product_11")
        cls.product7 = cls.env.ref("product.product_product_5")
        cls.backend = cls.env.ref("shopinvader.backend_1").with_context(
            bind_products_immediately=True
        )
        cls.backend2 = cls.env.ref("shopinvader.backend_2").with_context(
            bind_products_immediately=True
        )
        filter2 = cls.backend.product_assortment_id.copy()
        cls.backend2.product_assortment_id = filter2.id

    def test_all_backend(self):
        wizard = self.env["wizard.online_availability"].create(
            {"action_type": "exclude"}
        )
        with self.assertRaises(UserError) as ve:
            wizard.manage_availability()
            self.assertIn(
                "You need to select a backend or check the 'all backends' option",
                ve.exception.name,
            )
        backends = self.env["shopinvader.backend"].search(
            [("product_assortment_id", "<>", False)]
        )
        for backend in backends:
            backend.product_assortment_id.write(
                {
                    "blacklist_product_ids": [(5, False, False)],
                }
            )
            self.assertEqual(
                len(backend.product_assortment_id.blacklist_product_ids.ids), 0
            )

        wizard = (
            self.env["wizard.online_availability"]
            .with_context(active_ids=[self.product1.id, self.product2.id])
            .create({"action_type": "exclude", "all_backend": True})
        )
        wizard.manage_availability()

        for backend in backends:
            self.assertEqual(
                len(backend.product_assortment_id.blacklist_product_ids.ids), 2
            )
            self.assertListEqual(
                sorted(backend.product_assortment_id.blacklist_product_ids.ids),
                sorted([self.product1.id, self.product2.id]),
            )

        wizard = (
            self.env["wizard.online_availability"]
            .with_context(active_ids=[self.product3.id])
            .create({"action_type": "exclude", "all_backend": True})
        )
        wizard.manage_availability()

        for backend in backends:
            self.assertEqual(
                len(backend.product_assortment_id.blacklist_product_ids.ids), 3
            )
            self.assertListEqual(
                sorted(backend.product_assortment_id.blacklist_product_ids.ids),
                sorted([self.product1.id, self.product2.id, self.product3.id]),
            )

        wizard = (
            self.env["wizard.online_availability"]
            .with_context(active_ids=[self.product3.id])
            .create({"action_type": "include", "all_backend": True})
        )
        wizard.manage_availability()

        for backend in backends:
            self.assertEqual(
                len(backend.product_assortment_id.blacklist_product_ids.ids), 2
            )
            self.assertListEqual(
                sorted(backend.product_assortment_id.blacklist_product_ids.ids),
                sorted([self.product1.id, self.product2.id]),
            )

        wizard = (
            self.env["wizard.online_availability"]
            .with_context(active_ids=[self.product1.id, self.product2.id])
            .create({"action_type": "include", "all_backend": True})
        )
        wizard.manage_availability()

        for backend in backends:
            self.assertEqual(
                len(backend.product_assortment_id.blacklist_product_ids.ids), 0
            )

    def test_one_backend(self):

        backends = self.env["shopinvader.backend"].search(
            [("product_assortment_id", "<>", False)]
        )
        for backend in backends:
            backend.product_assortment_id.write(
                {
                    "blacklist_product_ids": [(5, False, False)],
                }
            )
            self.assertEqual(
                len(backend.product_assortment_id.blacklist_product_ids.ids), 0
            )

        wizard = (
            self.env["wizard.online_availability"]
            .with_context(active_ids=[self.product1.id, self.product2.id])
            .create(
                {"action_type": "exclude", "backend_ids": [(6, 0, [self.backend.id])]}
            )
        )

        wizard.manage_availability()

        self.assertEqual(
            len(self.backend.product_assortment_id.blacklist_product_ids.ids), 2
        )
        self.assertEqual(
            len(self.backend2.product_assortment_id.blacklist_product_ids.ids), 0
        )
