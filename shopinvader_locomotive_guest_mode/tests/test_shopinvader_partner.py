# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.addons.shopinvader_locomotive.tests.test_shopinvader_partner import (
    CommonShopinvaderPartner,
)


class TestShopinvaderPartnerGuest(CommonShopinvaderPartner):
    def setUp(self, *args, **kwargs):
        super(TestShopinvaderPartnerGuest, self).setUp(*args, **kwargs)
        self.backend2 = self.backend.search(
            [("id", "!=", self.backend.id)], limit=1
        )
        backends = self.backend
        backends |= self.backend2
        backends.write({"is_guest_mode_allowed": True})

    def _create_shopinvader_guest_for_partner(self, partner, backend=False):
        backend = backend or self.backend
        self._init_job_counter()
        shopinvader_partner = self.env["shopinvader.partner"].create(
            {
                "record_id": partner.id,
                "backend_id": backend.id,
                "is_guest": True,
            }
        )
        # The creation of a shopinvader partner into odoo must trigger
        # the creation of a user account into locomotive
        self._check_nbr_job_created(0)
        return shopinvader_partner

    def _create_shopinvader_guest_partner(self, data, backend=False):
        partner = self.env["res.partner"].create(data)
        return self._create_shopinvader_guest_for_partner(
            partner, backend=backend
        )

    def test_get_binding_to_export1(self):
        """
        Ensure the function _get_binding_to_export() correctly return
        shopinvader.partner related to current partner.
        :return:
        """
        shop_partner_guest = self._create_shopinvader_guest_partner(self.data)
        partner = shop_partner_guest.record_id
        self.assertNotIn(shop_partner_guest, partner._get_binding_to_export())
        partner.write({"name": "have a new name"})
        self._check_nbr_job_created(0)
        return

    def test_get_binding_to_export2(self):
        """
        Ensure the function _get_binding_to_export() correctly return
        shopinvader.partner related to current partner.
        :return:
        """
        shop_partner, params = self._create_shopinvader_partner(
            self.data, u"5a953d6aae1c744cfcfb3cd3"
        )
        partner = shop_partner.record_id
        shop_partner_guest = self._create_shopinvader_guest_for_partner(
            partner, backend=self.backend2
        )
        result_export = partner._get_binding_to_export()
        self.assertIn(shop_partner, result_export)
        self.assertNotIn(shop_partner_guest, result_export)
        partner.write({"name": "have a new name"})
        self._check_nbr_job_created(1)
        return
