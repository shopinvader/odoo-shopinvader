# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# pylint: disable=method-required-super


from odoo.addons.shopinvader_v1_base.tests.common import CommonCase


class ProductCommonCase(CommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.backend.bind_all_product()
        cls.template = cls.env.ref("product.product_product_4_product_template")
        cls.variant = cls.env.ref("product.product_product_4b")
        cls.template.taxes_id = cls.env.ref("shopinvader_v1_base.tax_1")
        cls.shopinvader_variants = cls.env["shopinvader.variant"].search(
            [
                ("record_id", "in", cls.template.product_variant_ids.ids),
                ("backend_id", "=", cls.backend.id),
            ]
        )
        cls.shopinvader_variant = cls.env["shopinvader.variant"].search(
            [
                ("record_id", "=", cls.variant.id),
                ("backend_id", "=", cls.backend.id),
            ]
        )
        cls.env.user.company_id.currency_id = cls.env.ref("base.USD")
        cls.base_pricelist = cls.env.ref("product.list0")
        cls.base_pricelist.currency_id = cls.env.ref("base.USD")
        cls.shopinvader_variant.record_id.currency_id = cls.env.ref("base.USD")
