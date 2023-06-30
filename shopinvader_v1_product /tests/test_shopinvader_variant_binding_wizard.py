# Copyright 2016 Cédric Pigeon
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tools import mute_logger

from odoo.addons.component.tests.common import SavepointComponentCase


@mute_logger("odoo.models.unlink")
@mute_logger("odoo.addons.base.models.ir_model")
class TestShopinvaderVariantBindingWizard(SavepointComponentCase):
    @classmethod
    def setUpClass(cls):
        super(TestShopinvaderVariantBindingWizard, cls).setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                tracking_disable=True,
                test_queue_job_no_delay=True,
            )
        )
        cls.backend = cls.env.ref("shopinvader.backend_1")
        cls.template = cls.env.ref("product.product_product_4_product_template")
        cls.variant = cls.env.ref("product.product_product_4b")
        cls.bind_wizard_model = cls.env["shopinvader.variant.binding.wizard"]
        cls.unbind_wizard_model = cls.env["shopinvader.variant.unbinding.wizard"]
        cls.product_bind_model = cls.env["shopinvader.variant"]

    def test_product_binding(self):
        """
        Select a product and
        - bind it to a shopinvader backend
          check that only the selected variant is binded (and the template)
          but not the other variants
        - bind the others variants
        - unbind it
        - bind it again
        """
        self.assertFalse(self.template.shopinvader_bind_ids)
        self.assertFalse(
            self.template.mapped("product_variant_ids.shopinvader_bind_ids")
        )

        # --------------------------------
        # Bind the product to the Backend
        # --------------------------------
        bind_wizard = self.bind_wizard_model.create(
            {
                "backend_id": self.backend.id,
                "product_ids": [(6, 0, [self.variant.id])],
            }
        )

        bind_wizard.bind_products()

        # A binding record should exists
        bind_record = self.product_bind_model.search(
            [
                ("record_id", "=", self.variant.id),
                ("backend_id", "=", self.backend.id),
            ]
        )

        self.assertEqual(len(bind_record), 1)
        self.assertEqual(bind_record, self.variant.shopinvader_bind_ids)

        # The template must be binded
        self.assertEqual(1, len(self.template.shopinvader_bind_ids))

        # only one variant must be binded
        self.assertEqual(
            1,
            len(self.template.mapped("product_variant_ids.shopinvader_bind_ids")),
        )

        # ------------------------
        # Bind the others variants
        # ------------------------
        variants = self.template.product_variant_ids - self.variant
        self.assertFalse(variants.mapped("shopinvader_bind_ids"))
        bind_wizard = self.bind_wizard_model.create(
            {
                "backend_id": self.backend.id,
                "product_ids": [(6, 0, variants.ids)],
            }
        )
        bind_wizard.bind_products()

        # now all the variants are binded
        self.assertTrue(variants.mapped("shopinvader_bind_ids"))
        self.assertEqual(
            len(self.template.product_variant_ids),
            len(self.template.shopinvader_bind_ids.shopinvader_variant_ids),
        )

        # --------------------------------
        # UnBind the product
        # --------------------------------
        unbind_wizard = self.unbind_wizard_model.create(
            {"shopinvader_variant_ids": [(6, 0, [bind_record.id])]}
        )
        unbind_wizard.unbind_products()

        # The binding record should be unreachable
        bind_record = self.product_bind_model.search(
            [
                ("record_id", "=", self.variant.id),
                ("backend_id", "=", self.backend.id),
            ]
        )

        self.assertEqual(len(bind_record), 0)

        # The binding record should still exist but inactive
        bind_record = self.product_bind_model.with_context(active_test=False).search(
            [
                ("record_id", "=", self.variant.id),
                ("backend_id", "=", self.backend.id),
            ]
        )

        self.assertEqual(len(bind_record), 1)

        # --------------------------------
        # Bind the product again
        # --------------------------------
        bind_wizard = self.bind_wizard_model.create(
            {
                "backend_id": self.backend.id,
                "product_ids": [(6, 0, [self.variant.id])],
            }
        )
        bind_wizard.bind_products()

        # The binding record should be re-activated
        bind_record = self.product_bind_model.search(
            [
                ("record_id", "=", self.variant.id),
                ("backend_id", "=", self.backend.id),
            ]
        )

        self.assertEqual(len(bind_record), 1)

    def test_product_inactivation(self):
        """
        Select a product and bind it to a Lengow Catalogue
        Inactivation of the product must unbind the product
        """
        # --------------------------------
        # Bind the product to the Backend
        # --------------------------------
        bind_wizard = self.bind_wizard_model.create(
            {
                "backend_id": self.backend.id,
                "product_ids": [(6, 0, [self.variant.id])],
            }
        )
        bind_wizard.bind_products()

        # A binding record should exists
        bind_record = self.product_bind_model.search(
            [
                ("record_id", "=", self.variant.id),
                ("backend_id", "=", self.backend.id),
            ]
        )

        self.assertEqual(len(bind_record), 1)

        # --------------------------------
        # Inactivate the product
        # --------------------------------
        self.variant.write({"active": False})

        # The binding record should be unreachable
        bind_record = self.product_bind_model.search(
            [
                ("record_id", "=", self.variant.id),
                ("backend_id", "=", self.backend.id),
            ]
        )

        self.assertEqual(len(bind_record), 0)

        # --------------------------------
        # Activate the product
        # --------------------------------
        self.variant.write({"active": True})

        # The binding record should be still unreachable
        bind_record = self.product_bind_model.search(
            [
                ("record_id", "=", self.variant.id),
                ("backend_id", "=", self.backend.id),
            ]
        )

        self.assertEqual(len(bind_record), 0)

        # ------------------------------------------------
        # Activate the binding and deactivate the template
        # -----------------------------------------------
        bind_wizard.bind_products()

        # A binding record should exists
        bind_record = self.product_bind_model.search(
            [
                ("record_id", "=", self.variant.id),
                ("backend_id", "=", self.backend.id),
            ]
        )

        self.assertTrue(bind_record)

        # deactivate the template
        self.template.write({"active": False})

        self.assertFalse(bind_record.active)
