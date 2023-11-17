# Copyright 2018 Akretion (http://www.akretion.com).
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# Copyright 2021 Camptocamp SA (https://www.camptocamp.com)
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.depends_context("se_backend")
    def _compute_sale_profile_id(self):
        """Compute sale_profile_id"""
        se_backend = self.env.context.get("se_backend", False)
        if not se_backend:
            return super()._compute_sale_profile_id()
        for partner in self:
            partner.sale_profile_id = partner._get_sale_profile(
                se_backend.sale_profile_ids,
                default=se_backend._get_default_profile(),
            )
