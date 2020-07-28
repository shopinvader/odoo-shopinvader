# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.addons.shopinvader.tests.common import ProductCommonCase


class TestCustomerSpecialProduct(ProductCommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.ir_export = cls.env.ref("shopinvader.ir_exp_shopinvader_variant")
        cls.parser = cls.ir_export.get_json_parser()
        cls.customer = cls.env.ref("base.res_partner_2")
        cls.shopinvader_variant.record_id.manufactured_for_partner_ids = [
            (6, 0, cls.customer.ids)
        ]

    def test_extra_fields(self):
        data = self.shopinvader_variant.jsonify(self.parser)[0]
        self.assertEqual(data["partners"], self.customer.ids)
