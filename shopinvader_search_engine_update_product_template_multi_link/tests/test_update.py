# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.shopinvader_search_engine_update.tests.common import (
    TestProductBindingUpdateBase,
)


class TestUpdate(TestProductBindingUpdateBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_template = cls.product.product_tmpl_id
        cls.product_template_2 = cls.env["product.template"].create({"name": "P2"})
        cls.product_2 = cls.product_template_2.product_variant_id

        cls.product_template_3 = cls.env["product.template"].create({"name": "P3"})
        cls.product_3 = cls.product_template_3.product_variant_id

        xmlid = "product_template_multi_link.product_template_link_type_up_selling"
        cls.link_type_up_sell = cls.env.ref(xmlid)
        cls.model = cls.env["product.template.link"]

        cls.product_binding_2 = cls.product_2._add_to_index(cls.se_index)
        cls.product_binding_3 = cls.product_3._add_to_index(cls.se_index)
        cls.product_bindings = (
            cls.product_binding + cls.product_binding_2 + cls.product_binding_3
        )
        cls.product_bindings.write({"state": "done"})

    def test_flow(self):
        # given
        vals = {
            "left_product_tmpl_id": self.product_template.id,
            "right_product_tmpl_id": self.product_template_2.id,
            "type_id": self.link_type_up_sell.id,
        }
        # when
        link = self.model.create(vals)
        # then
        self.assertEqual(self.product_binding.state, "to_recompute")
        self.assertEqual(self.product_binding_2.state, "to_recompute")
        self.assertEqual(self.product_binding_3.state, "done")

        # given
        self.product_bindings.write({"state": "done"})
        # when
        link.right_product_tmpl_id = self.product_template_3
        # then
        self.assertEqual(self.product_binding.state, "to_recompute")
        self.assertEqual(self.product_binding_3.state, "to_recompute")
        self.assertEqual(self.product_binding_2.state, "to_recompute")

        # given
        self.product_bindings.write({"state": "done"})
        # when
        link.unlink()
        # then
        self.assertEqual(self.product_binding.state, "to_recompute")
        self.assertEqual(self.product_binding_3.state, "to_recompute")
        self.assertEqual(self.product_binding_2.state, "done")
