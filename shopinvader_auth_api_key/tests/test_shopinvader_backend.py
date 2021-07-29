# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from psycopg2 import IntegrityError

from odoo.tools import mute_logger

from odoo.addons.shopinvader.tests import common


class TestShopinvaderBackend(common.CommonCase):
    @mute_logger("odoo.sql_db")
    def test_api_key_unique(self):
        backend1 = self.env.ref("shopinvader.backend_1")
        backend2 = self.env.ref("shopinvader.backend_2")

        with self.assertRaises(IntegrityError), self.env.cr.savepoint():
            backend2.write(
                {
                    "auth_api_key_id": backend1.auth_api_key_id.id,
                }
            )
            backend2.flush()

        backend2.write(
            {
                "auth_api_key_id": self.env.ref(
                    "shopinvader_auth_api_key.auth_api_key_2"
                ).id,
            }
        )
        backend2.flush()
