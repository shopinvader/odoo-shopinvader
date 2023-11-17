# Copyright 2018 Akretion (http://www.akretion.com).
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError

from .common import SaleProfileCommonCase


class TestPartner(SaleProfileCommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Osiris",
                "email": "osiris@shopinvader.com",
                "street": "pré du haut",
                "city": "Aurec sur Loire",
                "zip": "43110",
                "country_id": cls.env.ref("base.fr").id,
                "property_product_pricelist": cls.env.ref("product.list0").id,
            }
        )
        cls.env.ref("shopinvader_sale_profile.fiscal_position_0").write(
            {"zip_from": "43110", "zip_to": "43110"}
        )

    def test_get_sale_profile(self):
        # Case 1: pricelist and fposition match
        self.assertEqual(self.partner.sale_profile_id, self.sale_profile_1)
        # Case 2: pricelist empty and fposition match
        self.sale_profile_1.pricelist_id = False
        self.assertEqual(self.partner.sale_profile_id, self.sale_profile_1)
        # Case 3: pricelist match and fposition empty
        self.sale_profile_1.pricelist_id = self.env.ref("product.list0")
        self.sale_profile_1.fiscal_position_ids = False
        self.assertEqual(self.partner.sale_profile_id, self.sale_profile_1)
        # Case 4: pricelist and fposition empty
        self.sale_profile_1.pricelist_id = False
        self.assertEqual(self.partner.sale_profile_id, self.sale_profile_1)

    def test_get_sale_profile_no_default(self):
        # pricelist match but fposition not match and not empty
        self.partner.zip = False
        with self.assertRaises(UserError):
            # pylint: disable=pointless-statement
            self.partner.sale_profile_id
