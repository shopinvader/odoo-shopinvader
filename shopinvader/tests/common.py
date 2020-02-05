# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# pylint: disable=method-required-super

from contextlib import contextmanager

import mock
from odoo.addons.base_rest.controllers.main import _PseudoCollection
from odoo.addons.base_rest.tests.common import BaseRestCase
from odoo.addons.component.core import WorkContext
from odoo.addons.component.tests.common import ComponentMixin
from odoo.addons.queue_job.job import Job
from odoo.addons.server_environment import serv_config
from odoo.exceptions import MissingError
from odoo.tests import SavepointCase

from .. import shopinvader_response


class CommonMixin(ComponentMixin):
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
        collection = _PseudoCollection("shopinvader.backend", self.env)
        yield WorkContext(
            model_name="rest.service.registration",
            collection=collection,
            **params
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

    def _bind_products(self, products, backend=None):
        backend = backend or self.backend
        bind_wizard_model = self.env["shopinvader.variant.binding.wizard"]
        bind_wizard = bind_wizard_model.create(
            {"backend_id": backend.id, "product_ids": [(6, 0, products.ids)]}
        )
        bind_wizard.bind_products()

    def _install_lang(self, lang_xml_id):
        lang = self.env.ref(lang_xml_id)
        wizard = self.env["base.language.install"].create({"lang": lang.code})
        wizard.lang_install()
        return lang


class CommonCase(SavepointCase, CommonMixin):

    # by default disable tracking suite-wise, it's a time saver :)
    tracking_disable = True

    @classmethod
    def setUpClass(cls):
        super(CommonCase, cls).setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context, tracking_disable=cls.tracking_disable
            )
        )
        CommonMixin._setup_backend(cls)
        cls.setUpComponent()

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
        return record._fields.get(field).convert_to_export(
            record[field], record
        )


class ProductCommonCase(CommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.template = cls.env.ref(
            "product.product_product_4_product_template"
        )
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
        base_price_list = cls.env.ref("product.list0")
        base_price_list.currency_id = cls.env.ref("base.USD")
        cls.shopinvader_variant.record_id.currency_id = cls.env.ref("base.USD")


class ShopinvaderRestCase(BaseRestCase):
    def setUp(self, *args, **kwargs):
        super(ShopinvaderRestCase, self).setUp(*args, **kwargs)
        self.backend = self.env.ref("shopinvader.backend_1")
        # To ensure multi-backend works correctly, we just have to create
        # a new one on the same company.
        self.backend_copy = self.env.ref("shopinvader.backend_2")
        self.api_key = "myApiKey"
        self.api_key2 = "myApiKey2"
        self.auth_api_key_name = self.AUTH_API_KEY_NAME
        self.auth_api_key_name2 = self.AUTH_API_KEY_NAME2
        if self.auth_api_key_name not in serv_config.sections():
            serv_config.add_section(self.auth_api_key_name)
            serv_config.set(self.auth_api_key_name, "user", "admin")
            serv_config.set(self.auth_api_key_name, "key", self.api_key)
        if self.auth_api_key_name2 not in serv_config.sections():
            serv_config.add_section(self.auth_api_key_name2)
            serv_config.set(self.auth_api_key_name2, "user", "admin")
            serv_config.set(self.auth_api_key_name2, "key", self.api_key2)
        self.backend.auth_api_key_name = self.auth_api_key_name2


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
            "odoo.addons.shopinvader.services."
            "abstract_download.content_disposition"
        ) as mocked_cd, mock.patch(
            "odoo.addons.shopinvader.services.abstract_download.request"
        ) as mocked_request:
            mocked_cd.return_value = "attachment; filename=test"
            make_response = mock.MagicMock()
            mocked_request.make_response = make_response
            service.download(target.id)
            self.assertEqual(1, make_response.call_count)
            content, headers = make_response.call_args[0]
            self.assertTrue(content)
            self.assertIn(
                ("Content-Disposition", "attachment; filename=test"), headers
            )

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
