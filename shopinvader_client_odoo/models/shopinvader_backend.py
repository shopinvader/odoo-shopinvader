# Copyright 2019 Camptocamp SA (http://www.camptocamp.com)
# Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ShopinvaderBackend(models.Model):
    _description = "Shopinvader Odoo Client Backend"
    _name = "shopinvader.backend"
    _inherit = ["shopinvader.backend", "connector.backend"]
    _backend_name = "odooclient"

    client_api_key = fields.Char(
        sparse="client_data", required=True,
        help="Odoo client API key matching an existing website."
    )
