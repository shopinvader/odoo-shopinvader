# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from ..services.lead import LeadService
from openerp.addons.shopinvader.tests.common import CommonCase
from openerp import models


class LeadCase(CommonCase):

    def setUp(self, *args, **kwargs):
        super(LeadCase, self).setUp(*args, **kwargs)
        self.service = self._get_service(LeadService, None)

    def test_create_lead(self):
        data = {
            'email': 'revolution@shopinvader.com',
            'name': 'Besoin d\'un nouveau site',
            'company': 'Adaptoo',
            'street': '1 Rue Henri Matisse',
            'zip': '84310',
            'city': 'MORIERES-LES-AVIGNON',
            'contact_name': 'La famille',
            'description': 'Help, on ne supporte plus magento',
            'country_id': self.env.ref('base.fr').id,
            'mobile': '0600000000',
            }
        check_data = data.copy()
        check_data.update({
            'partner_name': check_data.pop('company'),
            'email_from': check_data.pop('email'),
            })

        self.service.create(data)
        lead = self.env['crm.lead'].search([], order='id desc', limit=1)[0]
        for key in check_data:
            if isinstance(lead[key], models.Model):
                self.assertEqual(lead[key].id, check_data[key])
            else:
                self.assertEqual(lead[key], check_data[key])
