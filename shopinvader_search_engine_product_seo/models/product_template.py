# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ProductTemplate(models.Model):

    _inherit = "product.template"

    def _build_seo_title(self):
        """
        Build the SEO product name
        :return: str
        """
        self.ensure_one()
        index = self._context.get("index", False)
        if index:
            return "{} | {}".format(
                self.name or "", index.backend_id.seo_title_suffix or ""
            )
        return super()._build_seo_title()
