# Copyright 2022 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tools import sql


def migrate(cr, version):
    if not version or sql.column_exists(cr, "shopinvader_partner", "last_login_time"):
        return
    # Pre-create new column
    sql.create_column(cr, "shopinvader_partner", "last_login_time", "timestamp")
