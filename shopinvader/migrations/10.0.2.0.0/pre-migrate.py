# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def migrate(cr, version):
    """Update database from previous versions, after updating module."""
    openupgrade.rename_tables(
        cr=cr, table_spec=[("locomotive_backend", "shopinvader_backend")]
    )
    openupgrade.rename_models(
        cr=cr, model_spec=[("locomotive.backend", "shopinvader.backend")]
    )
    # remove blocking view
    cr.execute(
        """DELETE FROM ir_ui_view
        WHERE arch_db ilike '%locomotive_backend_ids%'"""
    )
