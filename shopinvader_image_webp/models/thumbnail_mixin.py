# Copyright 2021 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import models


class ThumbnailMixin(models.AbstractModel):
    _inherit = "thumbnail.mixin"

    def generate_odoo_thumbnail(self):
        if self.env.context.get("skip_generate_odoo_thumbnail"):
            return True

        return super().generate_odoo_thumbnail()
