# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ShopinvaderBackend(models.Model):
    _description = "Locomotive CMS Backend"
    _name = "shopinvader.backend"
    _inherit = ["shopinvader.backend", "connector.backend"]
    _backend_name = "locomotivecms"

    location = fields.Char(
        help="Locomotive URL (see Developers section Locomotive site)"
    )
    username = fields.Char(
        help="Locomotive user email (see Developers section in "
        "Locomotive site)"
    )
    password = fields.Text(
        help="Locomotive user API key (see Developers section in "
        "Locomotive site)"
    )
    handle = fields.Char(
        help="Locomotive site handle (see Developers section in "
        "Locomotive site)"
    )
    currency_ids = fields.Many2many(
        comodel_name="res.currency", string="Currency"
    )

    def synchronize_metadata(self):
        return self._export_metafields_store()

    @api.model
    def _scheduler_synchronize_currency(self, domain=None):
        if domain is None:
            domain = []
        return self.search(domain).synchronize_currency()

    def synchronize_currency(self):
        return self._export_metafields_store(fields=["currency_ids"])

    def _export_metafields_store(self, fields=None):
        for record in self:
            with record.work_on(record._name) as work:
                exporter = work.component(usage="record.exporter")
                exporter.run(fields=fields)
        return True
