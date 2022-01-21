# Copyright 2021 Akretion (https://www.akretion.com).
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.component.core import Component


class HelpdeskSettingsService(Component):
    _name = "helpdesk.settings.service"
    _inherit = "helpdesk.settings.service"
    _collection = "shopinvader.backend"
