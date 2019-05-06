# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# pylint: disable=missing-manifest-dependency

from os.path import dirname, join

from odoo.addons.shopinvader.tests.common import CommonCase
from vcr import VCR

vcr = VCR(cassette_library_dir=join(dirname(__file__), "cassettes"))


class CheckVatCase(CommonCase):
    def setUp(self, *args, **kwargs):
        super(CheckVatCase, self).setUp(*args, **kwargs)
        with self.work_on_services(partner=None) as work:
            self.service = work.component(usage="customer")

    def test_check_valid_vat_with_vies(self):
        vat_number = "FR86792377731"
        self.service.shopinvader_backend.company_id.vat_check_vies = True
        with vcr.use_cassette("success.json"):
            res = self.service.dispatch(
                "check_vat", params={"vat_number": vat_number}
            )
            # Address can change, we remove unstable data
            res.pop("address")
            self.assertEqual(
                res,
                {
                    "vat_number": vat_number,
                    "with_details": True,
                    "name": u"SARL AKRETION FRANCE",
                    "valid": True,
                },
            )

    def test_check_invalid_vat_with_vies(self):
        vat_number = "FR54348545954"
        self.service.shopinvader_backend.company_id.vat_check_vies = True
        with vcr.use_cassette("failure.json"):
            res = self.service.dispatch(
                "check_vat", params={"vat_number": vat_number}
            )
            self.assertEqual(res, {"valid": False, "vat_number": vat_number})

    def test_check_valid_vat_without_vies(self):
        vat_number = "FR86792377731"
        res = self.service.dispatch(
            "check_vat", params={"vat_number": vat_number}
        )
        self.assertEqual(res, {"valid": True, "vat_number": vat_number})

    def test_check_invalid_vat_without_vies(self):
        vat_number = "FR54348545954"
        res = self.service.dispatch(
            "check_vat", params={"vat_number": vat_number}
        )
        self.assertEqual(res, {"valid": False, "vat_number": vat_number})
