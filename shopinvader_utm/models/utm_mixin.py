# Copyright 2021 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import models


class UtmMixin(models.AbstractModel):
    _inherit = "utm.mixin"

    def shopinvader_add_utm(self, params):
        vals = {}
        for key in params.keys():
            record = self.env.get("utm." + key)
            if record is not None:
                param_id = record.search([("name", "=", params[key])], limit=1)
                vals[key + "_id"] = param_id
        if vals:
            self.write(vals)
