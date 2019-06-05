# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.component.core import Component


class LocomotiveBinder(Component):
    "Base Binder for locomotive"
    _name = "locomotive.binder"
    _inherit = ["base.binder", "base.locomotive.connector"]
    _odoo_field = "record_id"
