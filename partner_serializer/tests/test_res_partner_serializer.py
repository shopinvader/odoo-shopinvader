# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestResPartnerSerializer(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestResPartnerSerializer, cls).setUpClass()
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "ACSONE SA/NV",
                "ref": "TOP10",
                "street": "Val Benoit",
                "street2": "Quai Banning 6",
                "zip": "4000",
                "city": u"Liège",
                "phone": "+32 2 8883148",
                "mobile": "+32 2 8883149",
                "vat": "BE123456",
                "is_company": True,
                "country_id": cls.env.ref("base.be").id,
            }
        )
        cls.serializer = cls.env["res.partner.serializer"]

    def test_convert_to_address(self):
        json = self.serializer._to_json_address(self.partner)
        self.maxDiff = 2000
        expected = {
            "id": self.partner.id,
            "display_name": self.partner.display_name,
            "name": "ACSONE SA/NV",
            "ref": "TOP10",
            "street": "Val Benoit",
            "street2": "Quai Banning 6",
            "zip": "4000",
            "city": u"Liège",
            "phone": "+32 2 8883148",
            "mobile": "+32 2 8883149",
            "vat": "BE123456",
            "state": None,
            "type": "contact",
            "is_company": True,
            "country": {
                "code": self.env.ref("base.be").code,
                "id": self.env.ref("base.be").id,
                "name": self.env.ref("base.be").name,
            },
        }
        self.assertDictEqual(expected, json)
