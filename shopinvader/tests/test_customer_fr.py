# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from .common import CommonFR
from .test_customer import TestCustomerCommon


class CustomerFRTest(CommonFR, TestCustomerCommon):
    """
    This is intended to help different language testing.
    As it reloads all translations, do this in a separate Test class
    to gather those tests.
    """

    def test_customer_payment_term_get_fr(self):
        """
        Unlink actual cart
        Change partner payment terms
        Create a new cart
        Ensure that payment term is correct in fr
        """
        self.env = self.env(context=dict(self.env.context, lang="fr_FR"))
        self.partner_service_data["payment_term"] = self.env.ref("account.account_payment_term_immediate").display_name
        self.partner = self.partner.with_context(lang="fr_FR")
        with self.work_on_services(
            partner=self.partner, shopinvader_session=self.shopinvader_session
        ) as work:
            self.service = work.component(usage="customer")
        data = self.service.dispatch("get", params={})["data"]

        self.assertDictContainsSubset(self.partner_service_data, data)
