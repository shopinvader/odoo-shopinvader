# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import exceptions

from .common import CommonRatingCase


class RatingServiceCase(CommonRatingCase):
    def setUp(self):
        super().setUp()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_create_rating(self):
        # create rating as a logged user
        res = self.rate_service.dispatch("create", params=self.data.copy())
        self.assertTrue(res["created"])
        record = self.env["rating.rating"].search(
            [
                ("res_id", "=", self.product2.id),
                ("partner_id", "=", self.partner1.id),
                ("res_model", "=", "product.product"),
            ],
            limit=1,
        )
        self.assertEqual("Feedback text", record.feedback)
        # create rating as an Anonymous user
        with self.work_on_services(partner=None) as work:
            self.rate_service = work.component(usage="test_rating")

        with self.assertRaises(exceptions.UserError) as em:
            self.rate_service.dispatch("create", params=self.data.copy())
        self.assertEqual(
            "Must be authenticated to create a rating", em.exception.args[0]
        )

    def test_delete_rating(self):
        res = self.rate_service.dispatch("delete", self.record.id)
        self.assertTrue(res["deleted"])
        self.assertFalse(self.record.active)
        # a partner cannot delete the rating of another
        with self.work_on_services(partner=self.partner2) as work:
            self.rate_service = work.component(usage="test_rating")

        with self.assertRaises(exceptions.UserError) as em:
            self.rate_service.dispatch("delete", self.record.id)
        self.assertEqual(
            "The record does not exist or you cannot delete it", em.exception.args[0]
        )

    def test_update(self):
        params = {"rating": 1, "feedback": "test"}
        res = self.rate_service.dispatch("update", self.record.id, params=params)
        self.assertTrue(res["updated"])
        self.assertEqual(1, self.record.rating)
        self.assertEqual("test", self.record.feedback)
        # a partner cannot update the rating of another
        with self.work_on_services(partner=self.partner2) as work:
            self.rate_service = work.component(usage="test_rating")

        with self.assertRaises(exceptions.UserError) as em:
            self.rate_service.dispatch("update", self.record.id, params=params)
        self.assertEqual(
            "The record does not exist or you cannot update it", em.exception.args[0]
        )

    def test_create_notification_for_service(self):
        service_notifications = self.env[
            "shopinvader.notification"
        ]._get_selection_rating()
        # product_product should be changed with a fake model for testing
        self.assertIn("rating_created_product_product", service_notifications)
        self.assertIn(
            "rating_publisher_response_product_product", service_notifications
        )
