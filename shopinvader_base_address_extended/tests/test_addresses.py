# Copyright 2022 KMEE (http://www.kmee.com.br).
# @author Cristiano Rodrigues <cristiano.rodrigues@kmee.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader.tests.common import CommonCase


class TestShopinvaderControllerCase(CommonCase):
    def setUp(self, *args, **kwargs):
        super(TestShopinvaderControllerCase, self).setUp(*args, **kwargs)
        with self.work_on_services(
            partner=None, shopinvader_session=self.shopinvader_session
        ) as work:
            self.addresses_service = work.component(usage="addresses")

    def test_json_parser(self):
        result = self.addresses_service._json_parser()
        self.assertIn("district", result)
        self.assertIn("street_number", result)
        self.assertIn("street_name", result)
        self.assertNotIn("street", result)
        self.assertNotIn("city", result)
        self.assertIn(("city_id", ["id", "name"]), result)

    def test_validator_create(self):
        result = self.addresses_service._validator_create()
        # Check additional settings, such as required, only for creation
        self._validate_assert(result)
        self.assertFalse(result["zip"]["required"])
        self.assertFalse(result["country"]["required"])
        self.assertFalse(result["district"]["required"])
        self.assertFalse(result["street_number"]["required"])
        self.assertFalse(result["street_name"]["required"])
        self.assertFalse(result["city_id"]["schema"]["id"]["nullable"])
        self.assertFalse(result["city_id"]["schema"]["name"]["nullable"])

    def test_validator_update(self):
        result = self.addresses_service._validator_update()
        self._validate_assert(result)

    def _validate_assert(self, result):
        self.assertIsInstance(result, dict)
        # Check that specific changes have been made to the result
        self.assertNotIn("street", result)
        self.assertNotIn("city", result)
        self.assertNotIn("state", result)
        self.assertIn("zip", result)
        self.assertIn("country", result)
        self.assertIn("district", result)
        self.assertIn("street_number", result)
        self.assertIn("street_name", result)
        self.assertIn("city_id", result)
        self.assertIsInstance(result["district"], dict)
        self.assertIsInstance(result["street_number"], dict)
        self.assertIsInstance(result["street_name"], dict)
        self.assertIsInstance(result["city_id"], dict)

        # Check the details of the added fields
        self.assertEqual(result["street_number"]["type"], "string")
        self.assertEqual(result["street_name"]["type"], "string")
        self.assertEqual(result["city_id"]["type"], "dict")
        self.assertIsInstance(result["city_id"]["schema"], dict)
        self.assertIn("id", result["city_id"]["schema"])
        self.assertIn("name", result["city_id"]["schema"])
