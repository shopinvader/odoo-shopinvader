# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def pre_init_hook(cr):
    """Loaded before installing the module.
    :param odoo.sql_db.Cursor cr:
        Database cursor.

    """
    # Moved fields from shopinvader
    openupgrade.update_module_moved_fields(
        cr, "sale.order", ["typology"], "shopinvader", "sale_cart"
    )
