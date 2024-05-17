# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from itertools import groupby

from odoo import models


class IrTranslation(models.Model):
    _inherit = "ir.translation"

    def write(self, vals):
        # Because updating translations from the wizard writes directly on
        # ir.translation, updating a product's name translation does not trigger
        # the computation of the url.
        # To fix that, adding a hook here, filtering as soon and as much as possible
        # translation records in order to avoid too much extra cost.
        res = super().write(vals)
        tmpl_name_records = self.filtered(
            lambda record: record.name == "product.template,name"
        )
        if not tmpl_name_records:
            return res
        sorted_records = tmpl_name_records.sorted(lambda record: record.lang)
        translation_groups = groupby(sorted_records, key=lambda record: record.lang)
        for lang_name, translation_list in translation_groups:
            lang = self.env["res.lang"]._lang_get(lang_name)
            if not lang:
                continue
            templates = self.env["product.template"].browse(
                [translation.res_id for translation in translation_list]
            )
            template_bindings = templates.shopinvader_bind_ids.filtered(
                lambda tmpl: tmpl.lang_id == lang and tmpl.url_builder == "auto"
            )
            template_bindings._compute_automatic_url_key()
        return res
