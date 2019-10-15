# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.multi
    def _get_binding_to_export(self):
        """
        Inherit to restrict binding to export:
        - Exclude guest
        :return: shopinvader.partner recordset
        """
        bindings = super(ResPartner, self)._get_binding_to_export()
        bindings = bindings.filtered(lambda b: not b.is_guest)
        return bindings
