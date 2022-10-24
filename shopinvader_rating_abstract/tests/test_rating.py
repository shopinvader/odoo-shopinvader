# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import psycopg2

from odoo.tools import mute_logger

from .common import CommonRatingCase


class RatingCase(CommonRatingCase):
    @mute_logger("odoo.sql_db")
    def test_sql_constraint_range(self):
        data = self.data.copy()
        data["rating"] = 0
        with self.assertRaises(psycopg2.IntegrityError) as em:
            self.rate_service.dispatch("create", params=data)
        self.assertIn("rating_rating_rating_range_shopinvader", em.exception.pgerror)

    @mute_logger("odoo.sql_db")
    def test_sql_constraint_unique(self):
        self.rate_service.dispatch("create", params=self.data.copy())
        with self.assertRaises(psycopg2.IntegrityError) as em:
            self.rate_service.dispatch("create", params=self.data.copy())
        self.assertIn("rating_rating_rating_unique", em.exception.pgerror)
