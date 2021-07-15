# Copyright 2019 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader.tests.common import NotificationCaseMixin
from odoo.addons.shopinvader.tests.test_address import CommonAddressCase


class NotificationCustomerCase(CommonAddressCase, NotificationCaseMixin):
    def setUp(self):
        super().setUp()
        with self.work_on_services(
            partner=None, shopinvader_session=self.shopinvader_session
        ) as work:
            self.customer_service = work.component(usage="customer")

    def _create_customer(self, **kw):
        data = {
            "email": "new@customer.example.com",
            "external_id": "D5CdkqOEL",
            "name": "Purple",
            "street": "Rue du jardin",
            "zip": "43110",
            "city": "Aurec sur Loire",
            "phone": "0485485454",
            "country": {"id": self.env.ref("base.fr").id},
        }
        data.update(kw)
        res = self.customer_service.dispatch("create", params=data)["data"]
        return self.env["res.partner"].browse(res["id"])

    def test_new_customer_welcome_not_validated(self):
        self.backend.update(
            dict(validate_customers=True, validate_customers_type="all")
        )
        partner = self._create_customer(
            email="new@tovalidate.example.com",
            external_id="F5CdkqOEL",
            name="To Validate",
        )
        job = self._find_notification_job(
            name="Notify new_customer_welcome_not_validated for res.partner,%d"
            % partner.id
        )
        self.assertTrue(job)
        self._perform_job(job)
        self._check_notification("new_customer_welcome_not_validated", partner)

        # now enable it
        invader_partner = partner._get_invader_partner(self.backend)
        invader_partner._get_shopinvader_validate_wizard().action_apply()
        job = self._find_notification_job(
            name="Notify customer_validated for res.partner,%d" % partner.id
        )
        self.assertTrue(job)
        self._perform_job(job)
        self._check_notification("customer_validated", partner)

    def test_address_created_not_validated(self):
        self.backend.update(
            dict(validate_customers=True, validate_customers_type="all")
        )
        params = dict(self.address_params, name="John Doe")
        self.address_service.dispatch("create", params=params)
        address = self.env["res.partner"].search([("name", "=", "John Doe")])
        self.assertEqual(address.parent_id, self.partner)
        # notification goes to the owner of the address
        partner = self.partner
        job = self._find_notification_job(
            name="Notify address_created_not_validated for res.partner,%d" % partner.id
        )
        self.assertTrue(job)
        self._perform_job(job)
        self._check_notification("address_created_not_validated", partner)

        # now enable it
        address._get_shopinvader_validate_address_wizard().action_apply()
        job = self._find_notification_job(
            name="Notify address_validated for res.partner,%d" % partner.id
        )
        self.assertTrue(job)
        self._perform_job(job)
        self._check_notification("address_validated", partner)
