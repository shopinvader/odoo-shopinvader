# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# Copyright 2019 Camptocamp SA (http://www.camptocamp.com)
# Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.component.core import AbstractComponent


class ClientConnectorComponent(AbstractComponent):
    """ Base Client Connector Component
    All components of this connector should inherit from it.
    """

    _name = "shopinvader.client.connector"
    _inherit = "base.connector"
    _collection = "shopinvader.backend"

    # TODO: is this used anywhere?
    _default_binding_fields = "client_bind_ids"
