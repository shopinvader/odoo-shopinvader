# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# Copyright 2019 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import CommonCase
from .test_address import CommonAddressCase


class NotificationCaseMixin(object):
    def _check_notification(self, notif_type, record):
        notif = self.env["shopinvader.notification"].search(
            [
                ("backend_id", "=", self.backend.id),
                ("notification_type", "=", notif_type),
            ]
        )
        vals = notif.template_id.generate_email(
            record.id,
            [
                "subject",
                "body_html",
                "email_from",
                "email_to",
                "partner_to",
                "email_cc",
                "reply_to",
                "scheduled_date",
            ],
        )
        message = self.env["mail.message"].search(
            [
                ("subject", "=", vals["subject"]),
                ("model", "=", record._name),
                ("res_id", "=", record.id),
            ]
        )
        self.assertEqual(len(message), 1)


class NotificationCartCase(CommonCase, NotificationCaseMixin):
    @classmethod
    def setUpClass(cls):
        super(NotificationCartCase, cls).setUpClass()
        cls.cart = cls.env.ref("shopinvader.sale_order_2")

    def test_cart_notification(self):
        self._init_job_counter()
        self.cart.action_confirm_cart()
        self._check_nbr_job_created(1)
        self._perform_created_job()
        self._check_notification("cart_confirmation", self.cart)

    def test_sale_notification(self):
        self.cart.action_confirm_cart()
        self._init_job_counter()
        self.cart.action_confirm()
        self._check_nbr_job_created(1)
        self._perform_created_job()
        self._check_notification("sale_confirmation", self.cart)

    def test_invoice_notification(self):
        self.cart.action_confirm_cart()
        self.cart.action_confirm()
        for line in self.cart.order_line:
            line.qty_delivered = line.product_uom_qty
        self.cart._create_invoices()
        self._init_job_counter()
        self.cart.invoice_ids._post()
        self._check_nbr_job_created(1)
        self._perform_created_job()
        self._check_notification("invoice_open", self.cart.invoice_ids[0])


class NotificationCustomerCase(CommonAddressCase, NotificationCaseMixin):
    def setUp(self, *args, **kwargs):
        super(NotificationCustomerCase, self).setUp(*args, **kwargs)
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

    def _find_job(self, **kw):
        leafs = dict(
            channel_method_name="<shopinvader.notification>.send",
            model_name="shopinvader.notification",
        )
        leafs.update(kw)
        domain = []
        for k, v in leafs.items():
            domain.append((k, "=", v))
        return self.env["queue.job"].search(domain, limit=1)

    def test_new_customer_welcome(self):
        partner = self._create_customer()
        job = self._find_job(
            name="Notify new_customer_welcome for res.partner,%d" % partner.id
        )
        self.assertTrue(job)
        self._perform_job(job)
        self._check_notification("new_customer_welcome", partner)

    def test_new_customer_welcome_not_validated(self):
        self.backend.update(
            dict(validate_customers=True, validate_customers_type="all")
        )
        partner = self._create_customer(
            email="new@tovalidate.example.com",
            external_id="F5CdkqOEL",
            name="To Validate",
        )
        job = self._find_job(
            name="Notify new_customer_welcome_not_validated for res.partner,%d"
            % partner.id
        )
        self.assertTrue(job)
        self._perform_job(job)
        self._check_notification("new_customer_welcome_not_validated", partner)

        # now enable it
        invader_partner = partner._get_invader_partner(self.backend)
        invader_partner._get_shopinvader_validate_wizard().action_apply()
        job = self._find_job(
            name="Notify customer_validated for res.partner,%d" % partner.id
        )
        self.assertTrue(job)
        self._perform_job(job)
        self._check_notification("customer_validated", partner)

    def test_address_created(self):
        params = dict(self.address_params, name="John Doe")
        self.address_service.dispatch("create", params=params)
        address = self.env["res.partner"].search([("name", "=", "John Doe")])
        self.assertEqual(address.parent_id, self.partner)
        # notification goes to the owner of the address
        partner = self.partner
        job = self._find_job(
            name="Notify address_created for res.partner,%d" % partner.id
        )
        self.assertTrue(job)
        self._perform_job(job)
        self._check_notification("address_created", partner)

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
        job = self._find_job(
            name="Notify address_created_not_validated for res.partner,%d" % partner.id
        )
        self.assertTrue(job)
        self._perform_job(job)
        self._check_notification("address_created_not_validated", partner)

        # now enable it
        address._get_shopinvader_validate_address_wizard().action_apply()
        job = self._find_job(
            name="Notify address_validated for res.partner,%d" % partner.id
        )
        self.assertTrue(job)
        self._perform_job(job)
        self._check_notification("address_validated", partner)

    def test_address_updated(self):
        params = dict(email="joe@foo.com")
        self.address_service.dispatch("update", self.address.id, params=params)
        # notification goes to the owner of the address
        partner = self.address.parent_id
        job = self._find_job(
            name="Notify address_updated for res.partner,%d" % partner.id
        )
        self.assertTrue(job)
        self._perform_job(job)
        self._check_notification("address_updated", partner)
