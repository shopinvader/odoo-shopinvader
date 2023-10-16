# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_search_engine.tests.common import TestProductBindingBase


class TestProductBindingUpdateBase(TestProductBindingBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_binding.state = "done"
