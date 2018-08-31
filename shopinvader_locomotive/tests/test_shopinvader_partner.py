# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import LocoCommonCase
import logging
_logger = logging.getLogger(__name__)

# pylint: disable=W7936
try:
    import requests_mock
except (ImportError, IOError) as err:
    _logger.debug(err)


class TestShopinvaderPartner(LocoCommonCase):

    def setUp(self, *args, **kwargs):
        super(TestShopinvaderPartner, self).setUp(*args, **kwargs)
        self.data = {
            'email': 'new@customer.example.com',
            'name': 'Purple',
            'street': 'Rue du jardin',
            'zip': '43110',
            'city': 'Aurec sur Loire',
            'phone': '0485485454',
            'country': {'id': self.env.ref('base.fr').id},
            }

    def _create_shopinvader_partner(self, data, external_id):
        partner = self.env['res.partner'].create(data)
        self._init_job_counter()
        shopinvader_partner = self.env['shopinvader.partner'].create({
            'record_id': partner.id,
            'backend_id': self.backend.id,
            })
        # The creation of a shopinvader partner into odoo must trigger
        # the creation of a user account into locomotive
        self._check_nbr_job_created(1)
        with requests_mock.mock() as m:
            m.post(
                self.base_url + '/tokens.json',
                json={'token': u'744cfcfb3cd3'})
            m.post(
                self.base_url + '/content_types/customers/entries',
                json={'_id': external_id})
            self._perform_created_job()
        return shopinvader_partner

    def test_create_shopinvader_partner_from_odoo(self):
        shop_partner = self._create_shopinvader_partner(
            self.data, u'5a953d6aae1c744cfcfb3cd3')
        self.assertEqual(
            shop_partner.external_id, u'5a953d6aae1c744cfcfb3cd3')

    def test_delete_shopinvader_partner_from_odoo(self):
        shop_partner = self._create_shopinvader_partner(
            self.data, u'5a953d6aae1c744cfcfb3cd3')
        self._init_job_counter()
        shop_partner.unlink()
        # The deletion of a shopinvader into odoo must trigger the deletion
        # of a user account into locomotive
        self._check_nbr_job_created(1)
        with requests_mock.mock() as m:
            m.post(
                self.base_url + '/tokens.json',
                json={'token': u'744cfcfb3cd3'})
            m.delete(
                self.base_url +
                '/content_types/customers/entries/5a953d6aae1c744cfcfb3cd3',
                json={})
            self._perform_created_job()
