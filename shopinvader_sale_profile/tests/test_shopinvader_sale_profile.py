# Copyright 2018 Akretion (http://www.akretion.com).
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.exceptions import ValidationError

from odoo.addons.shopinvader.tests.common import CommonCase


class TestShopinvaderSaleProfile(CommonCase):
    """
    Tests for shopinvader.sale.profile
    """

    def test_unique_default_sale_profile(self):
        """
        Test if an exception is raised if we try to set a second default
        sale profile.
        :return: bool
        """
        sale_profile = self.env.ref(
            "shopinvader_sale_profile.shopinvader_sale_profile_3"
        )
        with self.assertRaises(ValidationError):
            sale_profile.default = True
        return True

    def test_unique_pricelist_fposition_sale_profile(self):
        """
        Test if an exception is raised if we try to have more than 1
        pricelist per fiscal position.
        :return: bool
        """
        sale_profile = self.env.ref(
            "shopinvader_sale_profile.shopinvader_sale_profile_3"
        )
        fposition = self.env.ref("shopinvader.fiscal_position_0")
        with self.assertRaises(ValidationError):
            sale_profile.fiscal_position_ids = [(4, fposition.id)]
        return True
