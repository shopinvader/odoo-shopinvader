# Copyright 2022 KMEE INFORMATICA LTDA (http://www.kmee.com.br).
# @author Cristiano Rodrigues <cristiano.rodrigues@kmee.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader.tests.common import CommonCase


class TestShopinvaderControllerCase(CommonCase):
    def setUp(self, *args, **kwargs):
        super(TestShopinvaderControllerCase, self).setUp(*args, **kwargs)
        with self.work_on_services(
            partner=None, shopinvader_session=self.shopinvader_session
        ) as work:
            self.city_service = work.component(usage="city")

    def test_get_list_of_cities_by_state_code(self):
        params = {"state": "PR"}
        result = self.city_service.dispatch("search", params=params)
        country_id = self.env.ref("base.br")
        state_id = self.env["res.country.state"].search(
            [("country_id", "=", country_id.id), ("code", "=", "PR")]
        )
        city_ids = self.env["res.city"].search(
            [("country_id", "=", country_id.id), ("state_id", "=", state_id.id)]
        )
        cities = []
        for x in city_ids:
            cities.append({"name": x.name, "id": x.id})

        self.assertEqual(result, {"result": cities})
