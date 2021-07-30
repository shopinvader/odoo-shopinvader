# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ShopinvaderBackend(models.Model):
    _description = "Locomotive CMS Backend"
    _name = "shopinvader.backend"
    # do not change this order otherwise MRO will go nuts
    _inherit = ["connector.backend", "shopinvader.backend"]
    _backend_name = "locomotivecms"

    location = fields.Char(
        help="Locomotive URL (see Developers section Locomotive site)"
    )
    username = fields.Char(
        help="Locomotive user email (see Developers section in " "Locomotive site)"
    )
    password = fields.Text(
        help="Locomotive user API key (see Developers section in " "Locomotive site)",
        string="Locomotive's Api key",
    )
    handle = fields.Char(
        help="Locomotive site handle (see Developers section in " "Locomotive site)"
    )
    visible_filter_ids = fields.Many2many(
        comodel_name="product.filter", compute="_compute_visible_filter_ids"
    )

    @api.depends_context("lang")
    @api.depends("filter_ids.visible")
    def _compute_visible_filter_ids(self):
        for rec in self:
            rec.visible_filter_ids = rec.filter_ids.filtered(lambda x: x.visible)

    @property
    def _server_env_fields(self):
        env_fields = super()._server_env_fields
        env_fields.update({"username": {}, "password": {}, "handle": {}})
        return env_fields

    def synchronize_metadata(self):
        """
        Export metadatas managed by Odoo (countries, lang, currencies) to the
        website.

        :return:
        """
        return self._export_metafields_store()

    def reset_site_settings(self):
        """
        Initialize/reset the locomotive site settings (odoo url and api key)
        and synchronize metadata
        """
        self._export_metafields_store(force=True)

    @api.model
    def _scheduler_synchronize_currency(self, domain=None):
        if domain is None:
            domain = []
        return self.search(domain).synchronize_currency()

    def synchronize_currency(self):
        return self._export_metafields_store(fields=["currency_ids"])

    def _export_metafields_store(self, fields=None, force=False):
        for record in self:
            with record.work_on(record._name) as work:
                exporter = work.component(usage="record.exporter")
                exporter.run(fields=fields, force=force)
        return True
