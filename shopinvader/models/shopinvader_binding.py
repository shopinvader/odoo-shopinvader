# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ShopinvaderBinding(models.AbstractModel):
    _name = "shopinvader.binding"
    _description = "Shopinvader Binding"

    backend_id = fields.Many2one("shopinvader.backend", string="Backend", required=True)
    company_id = fields.Many2one(related="backend_id.company_id", store=True)
    external_id = fields.Char(string="External ID")
    sync_date = fields.Datetime(string="Last synchronization date")
    redirect_url_key = fields.Serialized(
        compute="_compute_redirect_url_key", string="Redirect Url Keys"
    )

    def _compute_redirect_url_key(self):
        for record in self:
            record.redirect_url_key = record.mapped("redirect_url_url_ids.url_key")
