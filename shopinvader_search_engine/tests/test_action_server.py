# Copyright 2020 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.queue_job.tests.common import JobMixin
from odoo.addons.shopinvader.tests.common import ProductCommonCase


class ActionServerCase(ProductCommonCase, JobMixin):
    def test_action_server_on_product_template(self):
        job = self.job_counter()
        # we take the number of variant linked => the number of created jobs
        bindings = self.env["shopinvader.product"].search([], limit=4)
        variant_length = len(bindings.mapped("shopinvader_variant_ids"))
        action = self.env.ref(
            "shopinvader_search_engine.action_recompute_shopinvader_product_on_template"
        )
        action_context = action.with_context(
            active_model="product.template",
            active_ids=bindings.mapped("record_id").ids,
        )
        action_context.run()
        self.assertEqual(job.count_created(), variant_length)

    def test_action_server_on_product_category(self):
        self.backend.bind_all_category()
        job = self.job_counter()
        bindings = self.env["shopinvader.category"].search([], limit=4)
        action = self.env.ref(
            "shopinvader_search_engine.action_recompute_shopinvader_category"
        )
        action_context = action.with_context(
            active_model="product.category",
            active_ids=bindings.mapped("record_id").ids,
        )
        action_context.run()
        self.assertEqual(job.count_created(), 4)
