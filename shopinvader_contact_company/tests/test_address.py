# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader.tests.test_address import (
    AddressTestCase,
    CommonAddressCase,
)


class CompanyAddressCase(CommonAddressCase, AddressTestCase):
    def setUp(self, *args, **kwargs):
        super(CompanyAddressCase, self).setUp(*args, **kwargs)
        self.address_params["company"] = "Licorne Corp"

    def check_data(self, address, data):
        # Passing the name in the service will be wrote
        # in the field contact_name
        data["contact_name"] = data.pop("name")
        return super(CompanyAddressCase, self).check_data(address, data)
