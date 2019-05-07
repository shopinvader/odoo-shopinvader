# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_locomotive.tests.test_shopinvader_partner import (
    CommonShopinvaderPartner,
)


class TestShopinvaderPartnerCompany(CommonShopinvaderPartner):
    def setUp(self, *args, **kwargs):
        super(TestShopinvaderPartnerCompany, self).setUp(*args, **kwargs)
        self.data["company"] = "Licorne Corp"

    def test_create_shopinvader_partner_from_odoo_with_company(self):
        # the name should not contain the company
        shop_partner, params = self._create_shopinvader_partner(
            self.data, u"5a953d6aae1c744cfcfb3cd3"
        )
        self.assertEqual(
            params,
            {
                u"content_entry": {
                    u"role": u"default",
                    u"email": u"new@customer.example.com",
                    u"name": u"Purple",
                }
            },
        )
        self.assertEqual(shop_partner.external_id, u"5a953d6aae1c744cfcfb3cd3")
