# Copyright 2019 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import mock
from odoo import exceptions
from odoo.addons.shopinvader_wishlist.tests.test_wishlist import (
    CommonWishlistCase,
)


class WishlistCase(CommonWishlistCase):
    @classmethod
    def setUpClass(cls):
        super(WishlistCase, cls).setUpClass()
        cls.company_binding = cls._create_invader_partner(
            cls.env,
            name="Company foo",
            external_id="company-foo",
            email="company@test.com",
            invader_user_token="company-user",
            is_company=True,
        )
        cls.user_binding = cls._create_invader_partner(
            cls.env,
            name="Simple user",
            external_id="simple-user",
            email="simpleuser@test.com",
            parent_id=cls.company_binding.record_id.id,
        )
        cls.prod_set = cls.env.ref("shopinvader_wishlist.wishlist_1").copy(
            {
                "shopinvader_backend_id": cls.backend.id,
                "partner_id": cls.company_binding.record_id.id,
            }
        )
        # get the right partner on the service
        cls.partner = cls.user_binding.record_id

    def test_add_to_cart(self):
        """As a simple user I can use the wishlist from my parent."""
        self.backend.multi_user_records_policy = "main_partner_id"
        prod = self.env.ref("product.product_product_4b")

        with self.work_on_services(
            partner=self.user_binding.record_id
        ) as work:
            cart_service = work.component(usage="cart")
        cart = cart_service._get()
        # no line yet
        self.assertFalse(cart.order_line)

        # make sure the wishlist service use the same cart
        with mock.patch.object(type(cart_service), "_get") as mocked:
            mocked.return_value = cart
            # Simulate normal behavior w/out our override
            with mock.patch.object(
                type(self.wishlist_service), "_allowed_order_partners"
            ) as mocked:
                mocked.return_value = self.env["res.partner"].browse()
                with self.assertRaises(exceptions.ValidationError) as err:
                    self.wishlist_service.add_to_cart(self.prod_set.id)
                self.assertEqual(
                    err.exception.name,
                    "You can use a sale order assigned "
                    "only to following partner(s): Company foo",
                )
            # make it work properly
            self.wishlist_service.add_to_cart(self.prod_set.id)
            self.assertEqual(cart.order_line[0].product_id, prod)
