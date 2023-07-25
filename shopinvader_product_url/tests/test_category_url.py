# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import TransactionCase


class TestCategoryUrl(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.lang_en = cls.env.ref("base.lang_en")
        cls.lang_fr = cls.env.ref("base.lang_fr")
        cls.lang_fr.active = True
        cls.categ_1 = (
            cls.env["product.category"]
            .with_context(lang="en_US")
            .create({"name": "Root"})
        )
        cls.categ_2 = (
            cls.env["product.category"]
            .with_context(lang="en_US")
            .create({"name": "Level 1", "parent_id": cls.categ_1.id})
        )
        cls.categ_3 = (
            cls.env["product.category"]
            .with_context(lang="en_US")
            .create({"name": "Level 2", "parent_id": cls.categ_2.id})
        )

    def _expect_url_for_lang(self, record, lang, url_key):
        self.assertEqual(record._get_main_url("global", lang).key, url_key)

    def test_url_for_main_categ(self):
        self.categ_1._update_url_key(lang="en_US")
        self._expect_url_for_lang(self.categ_1, "en_US", "root")

    def test_url_for_child(self):
        self.categ_3._update_url_key(lang="en_US")
        self._expect_url_for_lang(self.categ_1, "en_US", "root")
        self._expect_url_for_lang(self.categ_2, "en_US", "root/level-1")
        self._expect_url_for_lang(self.categ_3, "en_US", "root/level-1/level-2")

    def test_update_main(self):
        self.categ_3._update_url_key(lang="en_US")
        self.categ_1.name = "New Root"
        self.categ_3._update_url_key(lang="en_US")
        self._expect_url_for_lang(self.categ_1, "en_US", "new-root")
        self._expect_url_for_lang(self.categ_2, "en_US", "new-root/level-1")
        self._expect_url_for_lang(self.categ_3, "en_US", "new-root/level-1/level-2")

    def test_update_child(self):
        self.categ_3._update_url_key(lang="en_US")
        self.categ_2.name = "New Level 1"
        self.categ_3._update_url_key(lang="en_US")
        self._expect_url_for_lang(self.categ_1, "en_US", "root")
        self._expect_url_for_lang(self.categ_2, "en_US", "root/new-level-1")
        self._expect_url_for_lang(self.categ_3, "en_US", "root/new-level-1/level-2")
