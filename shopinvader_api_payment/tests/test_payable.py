# Copyright 2024 ACSONE SA (https://acsone.eu).
# @author Stéphane Bidoul <stephane.bidoul@acsone.eu>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase

from odoo.addons.shopinvader_api_payment.routers.utils import Payable


class TestPayable(TransactionCase):
    def test_payable_encode_decode(self):
        payable = Payable(
            payable_id=1,
            payable_model="account.move",
            payable_reference="INV/2020/001",
            amount=1000.0,
            amount_formatted="1\xa0000.00\xa0€",
            currency_id=1,
            partner_id=1,
            company_id=1,
        )
        encoded = payable.encode(self.env)
        decoded = Payable.decode(self.env, encoded)
        assert decoded == payable
