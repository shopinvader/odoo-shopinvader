from odoo.addons.shopinvader.tests.common import CommonCase
from odoo.addons.shopinvader.tests.test_cart_item import ItemCaseMixin


class ItemCase(ItemCaseMixin, CommonCase):
    @classmethod
    def setUpClass(cls):
        super(ItemCase, cls).setUpClass()
        cls._setup_products()

        cls.partner = cls.env.ref("shopinvader.partner_1")
        cls.cart = cls.env.ref("shopinvader.sale_order_2")

        cls.product_with_option = cls.env.ref(
            "sale_configurator_option.product_with_option"
        )
        cls.product_option_1 = cls.env.ref("sale_configurator_option.product_option_1")
        cls.product_option_2 = cls.env.ref("sale_configurator_option.product_option_2")
        cls.product_option_3 = cls.env.ref("sale_configurator_option.product_option_3")

    def setUp(self, *args, **kwargs):
        super(ItemCase, self).setUp(*args, **kwargs)
        self.shopinvader_session = {"cart_id": self.cart.id}
        with self.work_on_services(
            partner=self.partner, shopinvader_session=self.shopinvader_session
        ) as work:
            self.service = work.component(usage="cart")

    def test_add_item_option(self):
        self.remove_cart()
        last_order = self.env["sale.order"].search([], limit=1, order="id desc")

        # This does not work, because we can't add sol that creates child sol from the API
        # play_onchanges does not generate vals for childs in contrary to from the web interface

        cart = self.add_item(self.product_with_option.id, 2)
        self.assertGreater(cart["id"], last_order.id)
        self.assertEqual(len(cart["lines"]["items"]), 1)
        self.assertEqual(cart["lines"]["count"], 2)
        self.check_product_and_qty(
            cart["lines"]["items"][0], self.product_with_option.id, 2
        )
