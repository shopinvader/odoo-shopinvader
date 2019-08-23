# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# Copyright 2019 Camptocamp SA (http://www.camptocamp.com)
# Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo.addons.component.core import Component


class ClientBinder(Component):
    """Base Binder for shopinvader client"""
    _name = "shopinvader.client.binder"
    _inherit = ["base.binder", "shopinvader.client.connector"]
    _odoo_field = "record_id"
