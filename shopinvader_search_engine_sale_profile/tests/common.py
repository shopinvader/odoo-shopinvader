# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_sale_profile.tests.common import SaleProfileCommonCase
from odoo.addons.shopinvader_search_engine.tests.common import TestBindingIndexBase


class SaleProfileBackendCommonCase(SaleProfileCommonCase, TestBindingIndexBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.sale_profile_1.backend_id = cls.backend.id
        cls.sale_profile_2.backend_id = cls.backend.id
        cls.sale_profile_3.backend_id = cls.backend.id
