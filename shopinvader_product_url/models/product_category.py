# Copyright 2023 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models

from odoo.addons.shopinvader_base_url.models.abstract_url import DEFAULT_LANG


class ProductCategory(models.Model):
    _inherit = ["product.category", "abstract.url"]
    _name = "product.category"

    url_need_refresh = fields.Boolean(recursive=True)

    def _update_url_key(self, referential="global", lang=DEFAULT_LANG):
        # Ensure that parent url is up to date before updating the current url
        if self.parent_id:
            self.parent_id._update_url_key(referential=referential, lang=lang)
        return super()._update_url_key(referential=referential, lang=lang)

    def _generate_url_key(self, referential, lang):
        url_key = super()._generate_url_key(referential, lang)
        if self.parent_id:
            parent_url = self.parent_id._get_main_url(referential, lang)
            if parent_url:
                return "/".join([parent_url.key, url_key])
        return url_key

    def _compute_url_need_refresh_depends(self):
        return super()._compute_url_need_refresh_depends() + [
            "parent_id.url_need_refresh"
        ]
