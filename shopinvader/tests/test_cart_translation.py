from .test_cart import CommonConnectedCartCase


class TranslationCartCase(CommonConnectedCartCase):
    def setUp(self, *args, **kwargs):
        super(TranslationCartCase, self).setUp(*args, **kwargs)
        Langs = self.env["res.lang"].with_context(active_test=False)
        self.lang = Langs.search([("code", "=", "fr_FR")])
        self.lang.active = True
        self.env["ir.translation"].load_module_terms(
            ["base"], [self.lang.code]
        )

        self.cart = self.env.ref("shopinvader.sale_order_1").with_context(
            lang="fr_FR"
        )
        self.shopinvader_session = {"cart_id": self.cart.id}
        self.partner = self.backend.anonymous_partner_id
        self.product_1 = self.env.ref("product.product_product_4b")
        self.sale_obj = self.env["sale.order"]

        self.name_fr = "baguette"
        self.env["ir.translation"].create(
            {
                "type": "model",
                "name": "product.template,name",
                "module": "shopinvader",
                "lang": self.lang.code,
                "res_id": self.product_1.product_tmpl_id.id,
                "source": self.product_1.product_tmpl_id.name,
                "value": self.name_fr,
                "state": "translated",
            }
        )
        self.__class__.env = self.env(context={"lang": "fr_FR"})
        with self.work_on_services(
            partner=None, shopinvader_session=self.shopinvader_session,
        ) as work:
            self.service = work.component(usage="cart")

    def test_cart_translation(self):
        params = {"product_id": self.product_1.id, "item_qty": 1}
        self.service.shopinvader_session.clear()
        response = self.service.dispatch("add_item", params=params)
        cart = self.env["sale.order"].browse(response["data"]["id"])
        self.assertTrue(self.name_fr in cart.order_line.name)
