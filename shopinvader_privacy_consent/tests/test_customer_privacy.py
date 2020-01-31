# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import mock
from odoo import fields
from odoo.addons.shopinvader.tests.common import CommonCase


class CommonPrivacy(CommonCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        super(CommonPrivacy, cls).setUpClass(*args, **kwargs)
        cls.privacy_consent_obj = cls.env["privacy.consent"]
        vals = {"name": cls.backend.name}
        cls.partner = cls.env.ref("shopinvader.partner_1")
        cls.privacy_activity = cls.env["privacy.activity"].create(vals)
        vals = {
            "activity_id": cls.privacy_activity.id,
            "partner_id": cls.partner.id,
        }
        cls.privacy_consent = cls.privacy_consent_obj.create(vals)
        cls.backend.privacy_activity_id = cls.privacy_activity

    def setUp(self, *args, **kwargs):
        super(CommonPrivacy, self).setUp(*args, **kwargs)
        with self.work_on_services(
            partner=self.partner, shopinvader_session=self.shopinvader_session
        ) as work:
            self.service = work.component(usage="privacy")


class TestCustomerPrivacy(CommonPrivacy):
    def test_privacy_search(self):
        # The customer consent to privacy terms
        data = dict()
        res = self.service.dispatch("search", self.partner.id, params=data)[
            "data"
        ]

        self.assertDictContainsSubset(
            {"accepted": False, "accepted_date": None, "refusal_date": None},
            res[0],
        )

    def test_privacy_consent(self):
        now = "2020-01-30 12:00:00"
        data = {"consent": "true"}
        with mock.patch.object(fields.Datetime, "now") as mock_now:
            mock_now.return_value = now
            self.service.dispatch("consent", params=data)
        self.assertTrue(self.privacy_consent.accepted)
        self.assertEquals(now, self.privacy_consent.accepted_date)
        self.assertFalse(self.privacy_consent.refusal_date)
        self.assertEquals("answered", self.privacy_consent.state)
        res = self.service.dispatch("search", self.partner.id, params=data)[
            "data"
        ]

        self.assertDictContainsSubset(
            {"accepted": True, "accepted_date": now, "refusal_date": None},
            res[0],
        )

    def test_privacy_refusal(self):
        now = "2020-01-30 12:00:00"
        data = {"consent": False}
        with mock.patch.object(fields.Datetime, "now") as mock_now:
            mock_now.return_value = now
            self.service.dispatch("consent", params=data)
        self.assertFalse(self.privacy_consent.accepted)
        self.assertEquals(now, self.privacy_consent.refusal_date)
        self.assertFalse(self.privacy_consent.accepted_date)
        self.assertEquals("answered", self.privacy_consent.state)
        res = self.service.dispatch("search", self.partner.id, params=data)[
            "data"
        ]

        self.assertDictContainsSubset(
            {"accepted": False, "accepted_date": None, "refusal_date": now},
            res[0],
        )

    def test_privacy_consent_new(self):
        # No pre existing consent
        # Simulate check consent
        # A new consent is done
        self.privacy_consent.unlink()
        data = dict()
        res = self.service.dispatch("search", self.partner.id, params=data)[
            "data"
        ]

        self.assertEquals(res, [])

        now = "2020-01-30 12:00:00"
        data = {"consent": True}
        with mock.patch.object(fields.Datetime, "now") as mock_now:
            mock_now.return_value = now
            self.service.dispatch("consent", params=data)
        res = self.service.dispatch("search", self.partner.id, params=data)[
            "data"
        ]
        self.assertEquals(1, len(res))
        consent = self.privacy_consent_obj.browse(res[0].get("id"))
        self.assertEqual("answered", consent.state)
