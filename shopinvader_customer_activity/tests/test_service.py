# Copyright 2022 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import timedelta

from freezegun import freeze_time

from odoo import fields

from odoo.addons.shopinvader_restapi.tests.test_cart import CommonConnectedCartCase


class TestCartService(CommonConnectedCartCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.shopinvader_partner = self.partner.shopinvader_bind_ids

    def test_activity_date_logged(self):
        now = fields.Datetime.now()
        with freeze_time(now):
            self.service.dispatch("search")
            self.assertEqual(self.shopinvader_partner.first_active_date, now)
            self.assertEqual(self.shopinvader_partner.last_active_date, now)
        # Throttled writes
        after30s = now + timedelta(seconds=30)
        with freeze_time(after30s):
            self.service.dispatch("search")
            self.assertEqual(self.shopinvader_partner.first_active_date, now)
            self.assertEqual(self.shopinvader_partner.last_active_date, now)
        after5m = now + timedelta(minutes=5)
        with freeze_time(after5m):
            self.service.dispatch("search")
            self.assertEqual(self.shopinvader_partner.first_active_date, now)
            self.assertEqual(self.shopinvader_partner.last_active_date, after5m)
