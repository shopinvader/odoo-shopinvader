# Copyright 2026 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import CommonMassMailingCase


class TestMassMailing(CommonMassMailingCase):
    def test_subscribe(self):
        with self._create_test_client() as test_client:
            response = test_client.post(
                "/mass_mailing/subscribe",
                json={"name": "Test User", "email": "test-user@example.com"},
            )
        self.assertEqual(response.status_code, 200)
        contact = (
            self.env["mailing.contact"]
            .with_context(default_list_ids=(self.ml.id,))
            .search([("email_normalized", "=", "test-user@example.com")])
        )
        self.assertEqual(len(contact), 1)
        self.assertEqual(contact.name, "Test User")
        self.assertEqual(contact.email, "test-user@example.com")
        self.assertEqual(contact.list_ids, self.ml)
        self.assertFalse(contact.opt_out)

    def test_unsubscribe(self):
        contact = self.env["mailing.contact"].create(
            {
                "name": "Test User",
                "email": "test-user@example.com",
                "list_ids": [(6, 0, [self.ml.id])],
            }
        )
        self.assertFalse(contact.opt_out)
        with self._create_test_client() as test_client:
            response = test_client.post(
                "/mass_mailing/unsubscribe",
                json={"email": "test-user@example.com"},
            )
        self.assertEqual(response.status_code, 204)
        contact = contact.with_context(default_list_ids=(self.ml.id,)).browse(
            contact.id
        )
        self.env.invalidate_all()  # Invalidate cache since it is a stored rel
        self.assertTrue(contact.opt_out)

    def test_no_mailing_list_configured(self):
        self.endpoint.mailing_list_id = False
        with self._create_test_client(raise_server_exceptions=False) as test_client:
            response = test_client.post(
                "/mass_mailing/subscribe",
                json={"name": "Test User", "email": "test-user@example.com"},
            )
        self.assertEqual(response.status_code, 404)

    def test_unsubscribe_unknown_email(self):
        with self._create_test_client() as test_client:
            response = test_client.post(
                "/mass_mailing/unsubscribe",
                json={"email": "unknown@example.com"},
            )
        self.assertEqual(response.status_code, 204)

    def test_resubscribe(self):
        contact = self.env["mailing.contact"].create(
            {
                "name": "Test User",
                "email": "test-user@example.com",
                "list_ids": [(6, 0, [self.ml.id])],
            }
        )
        self.env.invalidate_all()  # Invalidate cache since it is a stored rel
        contact.subscription_list_ids.opt_out = True
        contact = contact.with_context(default_list_ids=(self.ml.id,)).browse(
            contact.id
        )

        self.assertTrue(contact.opt_out)
        with self._create_test_client() as test_client:
            response = test_client.post(
                "/mass_mailing/subscribe",
                json={"name": "Test User", "email": "test-user@example.com"},
            )
        self.assertEqual(response.status_code, 200)
        self.env.invalidate_all()  # Invalidate cache since it is a stored rel
        self.assertFalse(contact.opt_out)
