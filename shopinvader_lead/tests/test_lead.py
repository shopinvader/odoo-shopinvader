# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models

from odoo.addons.shopinvader_v1_base.tests.common import CommonCase
from odoo.addons.shopinvader_v1_base.tests.test_notification import (
    NotificationCaseMixin,
)


class LeadCase(CommonCase, NotificationCaseMixin):
    def _get_service(self, partner=None):
        with self.work_on_services(
            partner=partner, shopinvader_session=self.shopinvader_session
        ) as work:
            return work.component(usage="leads")

    def test_create_lead(self):
        data = {
            "email": "revolution@shopinvader.com",
            "name": "Besoin d'un nouveau site",
            "company": "Adaptoo",
            "street": "1 Rue Henri Matisse",
            "zip": "84310",
            "city": "MORIERES-LES-AVIGNON",
            "contact_name": "La famille",
            "description": "Help, on ne supporte plus magento",
            "country_id": self.env.ref("base.fr").id,
            "mobile": "0600000000",
        }
        check_data = data.copy()
        check_data.update(
            {
                "partner_name": check_data.pop("company"),
                "email_from": check_data.pop("email"),
            }
        )

        self._init_job_counter()
        service = self._get_service()
        service.dispatch("create", params=data)
        lead = self.env["crm.lead"].search([], order="id desc", limit=1)[0]
        for key in check_data:
            if isinstance(lead[key], models.Model):
                self.assertEqual(lead[key].id, check_data[key])
            else:
                self.assertEqual(lead[key], check_data[key])
        self._check_nbr_job_created(1)
        self._perform_created_job()
        self._check_notification("lead_confirmation", lead)

    def test_create_lead_with_logged_partner(self):
        partner = self.env.ref("shopinvader.partner_1")
        service = self._get_service(partner)
        data = {
            "name": "Besoin d'un nouveau site",
            "description": "Help, on ne supporte plus magento",
            "email": "bliblablo@example.org",
        }
        service.dispatch("create", params=data)
        lead = self.env["crm.lead"].search([], order="id desc", limit=1)
        self.assertEqual(lead.name, "Besoin d'un nouveau site")
        self.assertEqual(lead.partner_id.email, "osiris@shopinvader.com")
        self.assertEqual(lead.partner_id, partner)
