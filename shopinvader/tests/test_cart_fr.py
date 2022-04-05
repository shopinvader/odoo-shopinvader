# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tools import mute_logger

from .common import CommonFR
from .test_cart import CartClearTest, CommonConnectedCartCase


class ConnectedCartCaseFR(CommonFR, CommonConnectedCartCase, CartClearTest):
    """
    This is intended to help different language testing.
    As it reloads all translations, do this in a separate Test class
    to gather those tests.
    """

    @mute_logger("odoo.models.unlink")
    def test_cart_payment_term_get_fr(self):
        """
        Unlink actual cart
        Change partner payment terms
        Create a new cart
        Ensure that payment term is correct in fr
        """
        self.env = self.env(context=dict(self.env.context, lang="fr_FR"))
        self.partner.lang = "fr_FR"
        with self.work_on_services(
            partner=self.partner, shopinvader_session=self.shopinvader_session
        ) as work:
            self.service = work.component(usage="cart")
        self.cart.unlink()
        self.service._get()
        immediate = self.env.ref("account.account_payment_term_immediate")
        self.partner.property_payment_term_id = immediate
        cart_data = self.service.dispatch("search", params={})["data"]
        payment_term = cart_data.get("payment_term")
        self.assertEqual(payment_term, "Paiement immédiat")
