# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from .common import CommonCase


class BackendCase(CommonCase):
    @classmethod
    def setUpClass(cls):
        super(BackendCase, cls).setUpClass()
        cls.lang_fr = cls._install_lang(cls, "base.lang_fr")
        cls.env = cls.env(context=dict(cls.env.context, test_queue_job_no_delay=True))
        cls.backend = cls.backend.with_context(test_queue_job_no_delay=True)

    def _all_products_count(self):
        return self.env["product.template"].search_count([("sale_ok", "=", True)])

    def test_lookup_by_website_unique_key(self):
        website_unique_key = self.backend.website_unique_key
        self.assertTrue(website_unique_key)
        backend = self.env["shopinvader.backend"]._get_from_website_unique_key(
            website_unique_key
        )
        self.assertEqual(self.backend, backend)
        self.backend.website_unique_key = "new_key"
        backend = self.env["shopinvader.backend"]._get_from_website_unique_key(
            "new_key"
        )
        self.assertEqual(self.backend, backend)
