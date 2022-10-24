# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import exceptions

from odoo.addons.shopinvader_rating_abstract.tests.common import CommonRatingCase


class RatingCase(CommonRatingCase):
    def setUp(self):
        super().setUp()
        self.record = self.env["rating.rating"].create(self.params)
        with self.work_on_services(partner=self.partner1) as work:
            self.rate_service = work.component(usage="test_upvote")

        def _mock_synchronize(self):
            return None

        self.record._patch_method("synchronize_rating", _mock_synchronize)
        self.addCleanup(self.record._revert_method, "synchronize_rating")

    def test_upvote(self):
        self.assertEqual(0, self.record.votes)
        # the partner can't upvote his own rating
        with self.assertRaises(exceptions.UserError) as em:
            self.rate_service.dispatch("upvote", self.record.id)
        self.assertEqual(
            "The record does not exist or you cannot upvote it", em.exception.args[0]
        )

        with self.work_on_services(partner=self.partner2) as work:
            self.rate_service = work.component(usage="product_rating")

        res = self.rate_service.dispatch("upvote", self.record.id)
        self.assertTrue(res["upvoted"])
        self.assertEqual(1, self.record.votes)
        # the partner can only upvote a rating once
        res = self.rate_service.dispatch("upvote", self.record.id)
        self.assertFalse(res["upvoted"])
        self.assertEqual(1, self.record.votes)
