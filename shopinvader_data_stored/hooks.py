# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.jsonifier_stored.hooks import add_jsonifier_column


def pre_init_hook(cr):
    table_name = "shopinvader_variant"
    add_jsonifier_column(cr, table_name)
