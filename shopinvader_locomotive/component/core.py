# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import AbstractComponent


class BaseLocomotiveConnectorComponent(AbstractComponent):
    """Base Locomotive Connector Component
    All components of this connector should inherit from it.
    """

    _name = "base.locomotive.connector"
    _inherit = "base.connector"
    _collection = "shopinvader.backend"

    _default_binding_fields = "locomotive_bind_ids"
