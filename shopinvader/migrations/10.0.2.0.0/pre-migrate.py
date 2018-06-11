# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def migrate(cr, version):
    """Update database from previous versions, after updating module."""
    openupgrade.rename_models(
        cr=cr,
        model_spec=[('locomotive.backend', 'shopinvader.backend')]
    )
