# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

from odoo.tools.sql import column_exists, rename_column


def migrate(cr, version):
    if column_exists(cr, "res_partner", "shopinvader_enabled"):
        rename_column(
            cr, "res_partner", "shopinvader_enabled", "is_shopinvader_active"
        )
