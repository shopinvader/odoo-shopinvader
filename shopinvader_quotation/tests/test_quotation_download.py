# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader.tests.common import CommonCase, CommonTestDownload


class QuotationDownloadCase(CommonCase, CommonTestDownload):
    def setUp(self, *args, **kwargs):
        super(QuotationDownloadCase, self).setUp(*args, **kwargs)
        self.quotation = self.env.ref("shopinvader.sale_order_2")
        self.quotation.write({"typology": "quotation"})
        self.partner = self.env.ref("shopinvader.partner_1")
        with self.work_on_services(partner=self.partner) as work:
            self.service = work.component(usage="quotations")

    def test_quotation_download(self):
        self.assertEqual(self.quotation.typology, "quotation")
        self._test_download_allowed(self.service, self.quotation)
