# Copyright 2023 Akretion (https://www.akretion.com).
# @author Matthieu SAISON <matthieu.saison@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import json

from fastapi import status
from requests import Response

from odoo import models
from odoo.tests.common import tagged

from odoo.addons.extendable_fastapi.tests.common import FastAPITransactionCase

from ..routers.lead import leads_router


@tagged("post_install", "-at_install")
class TestShopinvaderLeadsApi(FastAPITransactionCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.test_partner = cls.env["res.partner"].create(
            {
                "name": "osiris",
                "street": "rue test",
                "zip": "1410",
                "city": "Waterloo",
                "country_id": cls.env.ref("base.be").id,
                "email": "osiris@shopinvader.com",
            }
        )
        cls.default_fastapi_authenticated_partner = cls.env["res.partner"]
        cls.default_fastapi_router = leads_router

    def test_create_lead(self):
        data = {
            "email": "revolution@shopinvader.com",
            "name": "Besoin d'un nouveau site",
            "company": "Adaptoo",
            "street": "1 Rue Henri Matisse",
            "zip": "84310",
            "city": "MORIERES-LES-AVIGNON",
            "contact_name": "La famille",
            "description": "<p>Help, on ne supporte plus magento</p>",
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
        with self._create_test_client() as test_client:
            response: Response = test_client.post("/leads", content=json.dumps(data))
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            msg=f"error message: {response.text}",
        )

        lead = self.env["crm.lead"].search([], order="id desc", limit=1)[0]
        for key in check_data:
            if isinstance(lead[key], models.Model):
                self.assertEqual(lead[key].id, check_data[key])
            else:
                self.assertEqual(lead[key], check_data[key])
        # TODO split shopinvader tests.test_notification
        # self._check_notification("lead_confirmation", lead)

    def test_create_lead_with_logged_partner(self):

        data = {
            "name": "Besoin d'un nouveau site",
            "description": "Help, on ne supporte plus magento",
            "email": "bliblablo@example.org",
        }
        with self._create_test_client(partner=self.test_partner) as test_client:
            response: Response = test_client.post("/leads", content=json.dumps(data))
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            msg=f"error message: {response.text}",
        )

        lead = self.env["crm.lead"].search([], order="id desc", limit=1)
        self.assertEqual(lead.name, "Besoin d'un nouveau site")
        self.assertEqual(lead.partner_id.email, "osiris@shopinvader.com")
        self.assertEqual(lead.partner_id, self.test_partner)
