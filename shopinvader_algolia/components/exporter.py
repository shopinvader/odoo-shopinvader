# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.component.core import Component


class AlgoliaExporter(Component):
    _name = "algolia.se.exporter"
    _inherit = ["se.exporter", "algolia.se.connector"]
    _apply_on = ["shopinvader.variant", "shopinvader.category"]
