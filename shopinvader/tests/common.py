# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# pylint: disable=method-required-super

from contextlib import contextmanager

import mock

from odoo import fields
from odoo.exceptions import MissingError
from odoo.tests import SavepointCase

from odoo.addons.base_rest.controllers.main import _PseudoCollection
from odoo.addons.base_rest.tests.common import BaseRestCase, RegistryMixin
from odoo.addons.component.core import WorkContext
from odoo.addons.component.tests.common import ComponentMixin
from odoo.addons.queue_job.job import Job

from .. import shopinvader_response
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
    def _bind_products(self, products, backend=None):
        backend = backend or self.backend
        bind_wizard_model = self.env["shopinvader.variant.binding.wizard"]
        bind_wizard = bind_wizard_model.create(
            {
                "backend_id": backend.id,
                "product_ids": [(6, 0, products.ids)],
                "run_immediately": True,
            }
        )
        bind_wizard.bind_products()

    def _refresh_json_data(self, products, backend=None):
        """Force recomputation of JSON data for given products.

        Especially helpful if your module adds new JSON keys
        but the product are already there and computed w/out your key.
        """
        if not products:
            return
        backend = backend or self.backend
        # TODO: remove hasattr check once `jsonify_stored` is ready.
        # The json-store machinery comes from search engine module.
        # We rely on it for product data BUT only
        # `shopinvader_search_engine` requires that dependency.
        # Hence, tests that need fresh product data because they add
        # new keys to ir.exports record will be broken w/out refresh
        # IF `shopinvader_search_engine` is installed (like on Travis).
        # `jsonify_stored` will extrapolate the feature
        # and allow to get rid of this hack.
        # For full story see
        # https://github.com/shopinvader/odoo-shopinvader/pull/783
        if not hasattr(self.env["shopinvader.variant"], "recompute_json"):
            return
        invader_variants = products
        if invader_variants._name == "product.product":
            invader_variants = products.shopinvader_bind_ids
        invader_variants.filtered_domain(
            [("backend_id", "=", backend.id)]
        ).recompute_json()

    def _install_lang(self, lang_xml_id):
        return _install_lang_odoo(self.env, lang_xml_id)

    @staticmethod
    def _create_invader_partner(env, **kw):
        values = {
            "backend_id": env.ref("shopinvader.backend_1").id,
        }
        values.update(kw)
        return env["shopinvader.partner"].create(values)


class CommonMixin(RegistryMixin, ComponentMixin, UtilsMixin):
    @staticmethod
    def _setup_backend(cls):
        cls.env = cls.env(context={"lang": "en_US"})
        cls.backend = cls.env.ref("shopinvader.backend_1")
        cls.backend.bind_all_product()
        cls.shopinvader_session = {}
        cls.existing_jobs = cls.env["queue.job"].browse()

    @contextmanager
    def work_on_services(self, **params):
        params = params or {}
        if params.get("partner") and not params.get("partner_user"):
            params["partner_user"] = params["partner"]
        if "shopinvader_backend" not in params:
            params["shopinvader_backend"] = self.backend
        if "shopinvader_session" not in params:
            params["shopinvader_session"] = {}
        if not params.get("partner_user") and params.get("partner"):
            params["partner_user"] = params["partner"]
        if params.get("partner_user"):
            params["invader_partner"] = params["partner_user"]._get_invader_partner(
                self.backend
            )
        # Safe defaults as these keys are mandatory for work ctx
        if "partner" not in params:
            params["partner"] = self.env["res.partner"].browse()
        if "partner_user" not in params:
            params["partner_user"] = self.env["res.partner"].browse()
        if "invader_partner" not in params:
            params["invader_partner"] = self.env["shopinvader.partner"].browse()
        collection = _PseudoCollection("shopinvader.backend", self.env)
        yield WorkContext(
            model_name="rest.service.registration", collection=collection, **params
        )

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
        CommonMixin._setup_backend(cls)
        cls.setUpComponent()
        cls.setUpRegistry()

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


class ProductCommonCase(CommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.template = cls.env.ref("product.product_product_4_product_template")
        cls.variant = cls.env.ref("product.product_product_4b")
        cls.template.taxes_id = cls.env.ref("shopinvader.tax_1")
        cls.shopinvader_variants = cls.env["shopinvader.variant"].search(
            [
                ("record_id", "in", cls.template.product_variant_ids.ids),
                ("backend_id", "=", cls.backend.id),
            ]
        )
        cls.shopinvader_variant = cls.env["shopinvader.variant"].search(
            [
                ("record_id", "=", cls.variant.id),
                ("backend_id", "=", cls.backend.id),
            ]
        )
        cls.env.user.company_id.currency_id = cls.env.ref("base.USD")
        cls.base_pricelist = cls.env.ref("product.list0")
        cls.base_pricelist.currency_id = cls.env.ref("base.USD")
        cls.shopinvader_variant.record_id.currency_id = cls.env.ref("base.USD")


class ShopinvaderRestCase(BaseRestCase):
    def setUp(self, *args, **kwargs):
        super(ShopinvaderRestCase, self).setUp(*args, **kwargs)
        self.backend = self.env.ref("shopinvader.backend_1")
        # To ensure multi-backend works correctly, we just have to create
        # a new one on the same company.
        self.backend_copy = self.env.ref("shopinvader.backend_2")


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
            "odoo.addons.shopinvader.services." "abstract_download.content_disposition"
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
