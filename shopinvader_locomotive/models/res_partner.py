# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def _get_binding_to_export(self):
        """
        Get every shopinvader partner to export
        :return: shopinvader.partner recordset
        """
        return self.mapped("shopinvader_bind_ids")
