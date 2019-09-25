# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import AbstractComponent


class LocomotiveExportMapper(AbstractComponent):
    _name = "locomotive.export.mapper"
    _inherit = ["base.locomotive.connector", "base.export.mapper"]
    _usage = "export.mapper"
