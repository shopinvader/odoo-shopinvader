# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class SaleProfileCommonCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.sale_profile_1 = cls.env["shopinvader.sale.profile"].create(
            {
                "pricelist_id": cls.env.ref("product.list0").id,
                "code": "public_tax_inc",
                "fiscal_position_ids": [
                    (
                        6,
                        0,
                        [cls.env.ref("shopinvader_sale_profile.fiscal_position_0").id],
                    )
                ],
            }
        )
        cls.sale_profile_2 = cls.env["shopinvader.sale.profile"].create(
            {
                "pricelist_id": cls.env.ref("shopinvader_sale_profile.pricelist_1").id,
                "code": "pro_tax_exc",
                "fiscal_position_ids": [
                    (
                        6,
                        0,
                        [
                            cls.env.ref(
                                "shopinvader_sale_profile.fiscal_position_1"
                            ).id,
                            cls.env.ref(
                                "shopinvader_sale_profile.fiscal_position_2"
                            ).id,
                        ],
                    )
                ],
            }
        )
        cls.sale_profile_3 = cls.env["shopinvader.sale.profile"].create(
            {
                "pricelist_id": cls.env.ref("product.list0").id,
                "code": "public_tax_exc",
                "fiscal_position_ids": [
                    (
                        6,
                        0,
                        [cls.env.ref("shopinvader_sale_profile.fiscal_position_2").id],
                    )
                ],
            }
        )
