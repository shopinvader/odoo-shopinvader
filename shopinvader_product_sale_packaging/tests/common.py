# Copyright 2023 Acsone SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class CommonPackagingCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(CommonPackagingCase, cls).setUpClass()
        cls.pkg_level_retail_box = cls.env["product.packaging.level"].create(
            {
                "name": "Retail Box",
                "code": "pack",
                "sequence": 3,
            }
        )
        cls.pkg_level_transport_box = cls.env["product.packaging.level"].create(
            {
                "name": "Transport Box",
                "code": "case",
                "sequence": 4,
            }
        )
        cls.pkg_level_pallet = cls.env["product.packaging.level"].create(
            {
                "name": "Pallet",
                "code": "pallet",
                "sequence": 5,
            }
        )
