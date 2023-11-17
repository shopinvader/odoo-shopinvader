# Copyright 2018 Akretion (http://www.akretion.com).
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_sale_profile.tests.test_partner import (
    TestPartner as BaseTestPartner,
)

from .common import SaleProfileBackendCommonCase


class TestPartner(SaleProfileBackendCommonCase, BaseTestPartner):
    def test_get_sale_profile_default(self):
        self.partner.zip = False
        self.sale_profile_3.default = True
        self.assertEqual(
            self.partner.with_context(se_backend=self.backend).sale_profile_id,
            self.sale_profile_3,
        )
