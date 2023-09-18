# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# pylint: disable=method-required-super

from contextlib import contextmanager

import mock

from odoo import fields
from odoo.exceptions import MissingError
from odoo.tests import SavepointCase

from odoo.addons.base_rest.controllers.main import RestController
from odoo.addons.base_rest.core import _rest_controllers_per_module
from odoo.addons.base_rest.tests.common import BaseRestCase, RegistryMixin
from odoo.addons.component.tests.common import ComponentMixin
from odoo.addons.queue_job.job import Job
from odoo.addons.shopinvader_restapi.models.track_external_mixin import (
    TrackExternalMixin,
)

from .. import shopinvader_response, utils
from ..services import abstract_download


def _install_lang_odoo(env, lang_xml_id, full_install=False):
    lang = env.ref(lang_xml_id)

    # Full install can be very expensive as it reloads EVERY translation
    # for EVERY installed module. 99.999% you don't need it for tests.
    if full_install:
        wizard = env["base.language.install"].create({"lang": lang.code})
        wizard.lang_install()
    else:
        lang.active = True
    return lang


class UtilsMixin(object):
    def _install_lang(self, lang_xml_id):
        return _install_lang_odoo(self.env, lang_xml_id)

    @staticmethod
    def _create_invader_partner(env, **kw):
        values = {
            "backend_id": env.ref("shopinvader_restapi.backend_1").id,
        }
        values.update(kw)
        return env["shopinvader.partner"].create(values)


class CommonMixin(RegistryMixin, ComponentMixin, UtilsMixin):
    @staticmethod
    def _setup_backend(cls):
        cls.env = cls.env(context={"lang": "en_US", "shopinvader_test": True})
        cls.backend = cls.env.ref("shopinvader_restapi.backend_1")
        cls.shopinvader_session = {}
        cls.existing_jobs = cls.env["queue.job"].browse()

    @contextmanager
    def work_on_services(self, **params):
        params = self._work_on_services_default_params(self, **params)
        with utils.work_on_service(self.env, **params) as work:
            yield work

    @staticmethod
    def _work_on_services_default_params(class_or_instance, **params):
        if "shopinvader_backend" not in params:
            params["shopinvader_backend"] = class_or_instance.backend
        if "shopinvader_session" not in params:
            params["shopinvader_session"] = {}
        utils.partner_work_context_defaults(
            class_or_instance.env, class_or_instance.backend, params
        )
        return params

    def _update_work_ctx(self, service, **params):
        params = self._work_on_services_default_params(self, **params)
        utils.update_work_ctx(service, params)

    def _init_job_counter(self):
        self.existing_jobs = self.env["queue.job"].search([])

    @property
    def created_jobs(self):
        return self.env["queue.job"].search([]) - self.existing_jobs

    def _check_nbr_job_created(self, nbr):
        self.assertEqual(len(self.created_jobs), nbr)

    def _perform_job(self, job):
        Job.load(self.env, job.uuid).perform()

    def _perform_created_job(self):
        for job in self.created_jobs:
            self._perform_job(job)


class CommonCase(SavepointCase, CommonMixin):

    # by default disable tracking suite-wise, it's a time saver :)
    tracking_disable = True

    @classmethod
    def setUpClass(cls):
        super(CommonCase, cls).setUpClass()
        cls.env = cls.env(
            context=dict(cls.env.context, tracking_disable=cls.tracking_disable)
        )

        class ControllerTest(RestController):
            _root_path = "/test_shopinvader/"
            _collection_name = "shopinvader.backend"
            _default_auth = "public"

        # Force service registration by the creation of a fake controller
        cls._ShopinvaderControllerTest = ControllerTest
        CommonMixin._setup_backend(cls)
        # TODO FIXME
        # It seem that setUpComponent / setUpRegistry loose stuff from
        # the cache so we do an explicit flush here to avoid losing data
        cls.env["base"].flush()
        cls.setUpComponent()
        cls.setUpRegistry()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        _rest_controllers_per_module["shopinvader_restapi"] = []

    def setUp(self):
        SavepointCase.setUp(self)
        CommonMixin.setUp(self)

        shopinvader_response.set_testmode(True)

        @self.addCleanup
        def cleanupShopinvaderResponseTestMode():
            shopinvader_response.set_testmode(False)

    def _get_selection_label(self, record, field):
        """
        Get the translated label of the record selection field
        :param record: recordset
        :param field: str
        :return: str
        """
        return record._fields.get(field).convert_to_export(record[field], record)

    def _get_last_external_update_date(self, record):
        if isinstance(record, TrackExternalMixin):
            return record.last_external_update_date
        return False

    def _check_last_external_update_date(self, record, previous_date):
        if isinstance(record, TrackExternalMixin):
            self.assertTrue(record.last_external_update_date)
            if previous_date:
                self.assertTrue(record.last_external_update_date > previous_date)


class ShopinvaderRestCase(BaseRestCase):
    def setUp(self, *args, **kwargs):
        super(ShopinvaderRestCase, self).setUp(*args, **kwargs)
        self.backend = self.env.ref("shopinvader_restapi.backend_1")
        # To ensure multi-backend works correctly, we just have to create
        # a new one on the same company.
        self.backend_copy = self.env.ref("shopinvader_restapi.backend_2")


class CommonTestDownload(object):
    """
    Dedicated class to test the download service.
    Into your test class, just inherit this one (python mode) and call
    correct function.
    """

    def _test_download_not_allowed(self, service, target):
        """
        Data
            * A target into an invalid/not allowed state
        Case:
            * Try to download the document
        Expected result:
            * MissingError should be raised
        :param service: shopinvader service
        :param target: recordset
        :return:
        """
        with self.assertRaises(MissingError):
            service.download(target.id)

    def _test_download_allowed(self, service, target):
        """
        Data
            * A target with a valid state
        Case:
            * Try to download the document
        Expected result:
            * An http response with the file to download
        :param service: shopinvader service
        :param target: recordset
        :return:
        """
        with mock.patch(
            "odoo.addons.shopinvader_restapi.services."
            "abstract_download.content_disposition"
        ) as mocked_cd:
            request = mock.MagicMock()
            abstract_download.request = request
            mocked_cd.return_value = "attachment; filename=test"
            # mocked_request.make_response = make_response
            service.download(target.id)
            self.assertEqual(1, request.make_response.call_count)
            content, headers = request.make_response.call_args[0]
            self.assertTrue(content)
            self.assertIn(("Content-Disposition", "attachment; filename=test"), headers)

    def _test_download_not_owner(self, service, target):
        """
        Data
            * A target into a valid state but doesn't belong to the connected
            user (from the service).
        Case:
            * Try to download the document
        Expected result:
            * MissingError should be raised
        :param service: shopinvader service
        :param target: recordset
        :return:
        """
        self._test_download_not_allowed(service, target)

    # FIXME: this seems duplicated in some common test cases

    def _ensure_posted(self, invoice):
        if invoice.state != "posted":
            invoice._post()

    def _make_payment(self, invoice):
        """
        Make the invoice payment
        :param invoice: account.invoice recordset
        :return: bool
        """
        self._ensure_posted(invoice)
        ctx = {"active_ids": invoice.ids, "active_model": "account.move"}
        wizard_obj = self.register_payments_obj.with_context(ctx)
        register_payments = wizard_obj.create(
            {
                "payment_date": fields.Date.today(),
                "journal_id": self.bank_journal_euro.id,
                "payment_method_id": self.payment_method_manual_in.id,
            }
        )
        register_payments._create_payments()


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

    def _find_notification_job(self, **kw):
        leafs = dict(
            channel_method_name="<shopinvader.notification>.send",
            model_name="shopinvader.notification",
        )
        leafs.update(kw)
        domain = []
        for k, v in leafs.items():
            domain.append((k, "=", v))
        return self.env["queue.job"].search(domain, limit=1)
