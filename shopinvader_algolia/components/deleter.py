# -*- coding: utf-8 -*-
# © 2019 Akretion (http://www.akretion.com)
# Benoît GUILLOt <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.component.core import Component


class AlgoliaDeleter(Component):
    _name = "algolia.se.deleter"
    _inherit = ["se.deleter", "algolia.se.connector"]
    _apply_on = ["shopinvader.variant"]
