# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# pylint: disable=method-required-super


from odoo.addons.shopinvader_restapi.tests.common import CommonCase


class ProductCommonCase(CommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.backend.bind_all_product()
        cls.template = cls.env.ref("product.product_product_4_product_template")
        cls.variant = cls.env.ref("product.product_product_4b")
        cls.template.taxes_id = cls.env.ref("shopinvader_restapi.tax_1")
        cls.shopinvader_variants = cls.env["shopinvader.variant"].search(
            [
                ("record_id", "in", cls.template.product_variant_ids.ids),
                ("backend_id", "=", cls.backend.id),
            ]
        )
        cls.shopinvader_variant = cls.env["shopinvader.variant"].search(
            [
                ("record_id", "=", cls.variant.id),
                ("backend_id", "=", cls.backend.id),
            ]
        )
        cls.env.user.company_id.currency_id = cls.env.ref("base.USD")
        cls.base_pricelist = cls.env.ref("product.list0")
        cls.base_pricelist.currency_id = cls.env.ref("base.USD")
        cls.shopinvader_variant.record_id.currency_id = cls.env.ref("base.USD")


class ProductUtilsMixin(CommonCase):
    def _bind_products(self, products, backend=None):
        backend = backend or self.backend
        bind_wizard_model = self.env["shopinvader.variant.binding.wizard"]
        bind_wizard = bind_wizard_model.create(
            {
                "backend_id": backend.id,
                "product_ids": [(6, 0, products.ids)],
                "run_immediately": True,
            }
        )
        bind_wizard.bind_products()

    def _refresh_json_data(self, products, backend=None):
        """Force recomputation of JSON data for given products.

        Especially helpful if your module adds new JSON keys
        but the product are already there and computed w/out your key.
        """
        if not products:
            return
        backend = backend or self.backend
        # TODO: remove hasattr check once `jsonify_stored` is ready.
        # The json-store machinery comes from search engine module.
        # We rely on it for product data BUT only
        # `shopinvader_search_engine` requires that dependency.
        # Hence, tests that need fresh product data because they add
        # new keys to ir.exports record will be broken w/out refresh
        # IF `shopinvader_search_engine` is installed (like on Travis).
        # `jsonify_stored` will extrapolate the feature
        # and allow to get rid of this hack.
        # For full story see
        # https://github.com/shopinvader/odoo-shopinvader/pull/783
        if not hasattr(self.env["shopinvader.variant"], "recompute_json"):
            return
        invader_variants = products
        if invader_variants._name == "product.product":
            invader_variants = products.shopinvader_bind_ids
        invader_variants.filtered_domain(
            [("backend_id", "=", backend.id)]
        ).recompute_json()
