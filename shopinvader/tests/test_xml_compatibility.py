# Copyright 2023 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import SavepointCase


class TestXMLID(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_xml_id_compatibility(self):
        product = self.env.ref("shopinvader.product_template_thelma")
        self.assertTrue(product)
